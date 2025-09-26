# Especificaciones Técnicas Detalladas - API de Bitácora

## Configuración Detallada de Base de Datos

### Esquema de Tabla Principal Optimizado

```sql
-- =====================================================
-- Tabla principal de bitácora con particionamiento
-- =====================================================
CREATE PARTITION FUNCTION PF_LogEntries_Date (datetime2)
AS RANGE RIGHT FOR VALUES (
    '2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01',
    '2024-05-01', '2024-06-01', '2024-07-01', '2024-08-01',
    '2024-09-01', '2024-10-01', '2024-11-01', '2024-12-01'
);

CREATE PARTITION SCHEME PS_LogEntries_Date 
AS PARTITION PF_LogEntries_Date 
TO ([FG_2024_01], [FG_2024_02], [FG_2024_03], [FG_2024_04],
    [FG_2024_05], [FG_2024_06], [FG_2024_07], [FG_2024_08],
    [FG_2024_09], [FG_2024_10], [FG_2024_11], [FG_2024_12]);

CREATE TABLE [dbo].[LogEntries] (
    [Id] BIGINT IDENTITY(1,1) NOT NULL,
    [EventTimestamp] DATETIME2(3) NOT NULL,
    [Tag] NVARCHAR(50) NOT NULL,
    [Description] NVARCHAR(MAX) NULL,
    [CreatedAt] DATETIME2(3) NOT NULL DEFAULT (SYSUTCDATETIME()),
    [CorrelationId] UNIQUEIDENTIFIER NOT NULL DEFAULT (NEWID()),
    [ProcessingStatus] TINYINT NOT NULL DEFAULT (0), -- 0=Pending, 1=Processed, 2=Failed
    [RetryCount] INT NOT NULL DEFAULT (0),
    [ClientId] NVARCHAR(50) NULL,
    [SourceApplication] NVARCHAR(100) NULL,
    [Severity] TINYINT NOT NULL DEFAULT (1), -- 1=Info, 2=Warning, 3=Error, 4=Critical
    [AdditionalData] NVARCHAR(MAX) NULL, -- JSON for flexible metadata
    [HashKey] AS (HASHBYTES('SHA2_256', CONCAT(EventTimestamp, Tag, Description))) PERSISTED,
    
    CONSTRAINT [PK_LogEntries] PRIMARY KEY CLUSTERED ([Id], [EventTimestamp])
        ON PS_LogEntries_Date([EventTimestamp])
) ON PS_LogEntries_Date([EventTimestamp]);

-- =====================================================
-- Índices optimizados para consultas frecuentes
-- =====================================================

-- Índice principal para consultas por timestamp y tag
CREATE NONCLUSTERED INDEX [IX_LogEntries_EventTimestamp_Tag_Includes]
ON [dbo].[LogEntries] ([EventTimestamp] DESC, [Tag] ASC)
INCLUDE ([Description], [CorrelationId], [Severity], [ClientId])
WITH (
    PAD_INDEX = OFF,
    STATISTICS_NORECOMPUTE = OFF,
    SORT_IN_TEMPDB = ON,
    DROP_EXISTING = OFF,
    ONLINE = ON,
    ALLOW_ROW_LOCKS = ON,
    ALLOW_PAGE_LOCKS = ON,
    FILLFACTOR = 90
) ON PS_LogEntries_Date([EventTimestamp]);

-- Índice para consultas por CorrelationId (tracking de transacciones)
CREATE NONCLUSTERED INDEX [IX_LogEntries_CorrelationId]
ON [dbo].[LogEntries] ([CorrelationId])
INCLUDE ([EventTimestamp], [Tag], [Description])
WITH (FILLFACTOR = 95) ON PS_LogEntries_Date([EventTimestamp]);

-- Índice para consultas por cliente y aplicación
CREATE NONCLUSTERED INDEX [IX_LogEntries_ClientId_SourceApp]
ON [dbo].[LogEntries] ([ClientId], [SourceApplication], [EventTimestamp] DESC)
INCLUDE ([Tag], [Severity])
WITH (FILLFACTOR = 90) ON PS_LogEntries_Date([EventTimestamp]);

-- Índice para deduplicación por hash
CREATE NONCLUSTERED INDEX [IX_LogEntries_HashKey_EventTimestamp]
ON [dbo].[LogEntries] ([HashKey], [EventTimestamp])
WITH (FILLFACTOR = 95) ON PS_LogEntries_Date([EventTimestamp]);

-- Índice columnstore para analytics y reporting
CREATE NONCLUSTERED COLUMNSTORE INDEX [NCIX_LogEntries_Analytics]
ON [dbo].[LogEntries] ([EventTimestamp], [Tag], [Severity], [ClientId], [SourceApplication])
ON PS_LogEntries_Date([EventTimestamp]);

-- =====================================================
-- Tabla de metadatos para optimización
-- =====================================================
CREATE TABLE [dbo].[LogTags] (
    [TagId] INT IDENTITY(1,1) PRIMARY KEY,
    [TagName] NVARCHAR(50) UNIQUE NOT NULL,
    [Category] NVARCHAR(30) NULL,
    [IsActive] BIT NOT NULL DEFAULT (1),
    [CreatedAt] DATETIME2(3) NOT NULL DEFAULT (SYSUTCDATETIME()),
    [UsageCount] BIGINT NOT NULL DEFAULT (0),
    [LastUsed] DATETIME2(3) NULL
);

CREATE UNIQUE NONCLUSTERED INDEX [IX_LogTags_TagName]
ON [dbo].[LogTags] ([TagName]) WHERE [IsActive] = 1;

-- =====================================================
-- Stored Procedures optimizados para bulk operations
-- =====================================================

CREATE OR ALTER PROCEDURE [dbo].[BulkInsertLogEntries]
    @LogData NVARCHAR(MAX) -- JSON array with log entries
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    
    DECLARE @TempTable TABLE (
        EventTimestamp DATETIME2(3),
        Tag NVARCHAR(50),
        Description NVARCHAR(MAX),
        CorrelationId UNIQUEIDENTIFIER,
        ClientId NVARCHAR(50),
        SourceApplication NVARCHAR(100),
        Severity TINYINT,
        AdditionalData NVARCHAR(MAX)
    );
    
    -- Parse JSON input
    INSERT INTO @TempTable
    SELECT 
        EventTimestamp,
        Tag,
        Description,
        CorrelationId,
        ClientId,
        SourceApplication,
        Severity,
        AdditionalData
    FROM OPENJSON(@LogData) WITH (
        EventTimestamp DATETIME2(3) '$.eventTimestamp',
        Tag NVARCHAR(50) '$.tag',
        Description NVARCHAR(MAX) '$.description',
        CorrelationId UNIQUEIDENTIFIER '$.correlationId',
        ClientId NVARCHAR(50) '$.clientId',
        SourceApplication NVARCHAR(100) '$.sourceApplication',
        Severity TINYINT '$.severity',
        AdditionalData NVARCHAR(MAX) '$.additionalData'
    );
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Bulk insert with minimal logging
        INSERT INTO [dbo].[LogEntries] WITH (TABLOCK) (
            EventTimestamp, Tag, Description, CorrelationId,
            ClientId, SourceApplication, Severity, AdditionalData
        )
        SELECT 
            EventTimestamp, Tag, Description, CorrelationId,
            ClientId, SourceApplication, Severity, AdditionalData
        FROM @TempTable;
        
        -- Update tag usage statistics
        WITH TagStats AS (
            SELECT Tag, COUNT(*) as UsageCount
            FROM @TempTable
            GROUP BY Tag
        )
        MERGE [dbo].[LogTags] AS target
        USING TagStats AS source ON target.TagName = source.Tag
        WHEN MATCHED THEN 
            UPDATE SET 
                UsageCount = target.UsageCount + source.UsageCount,
                LastUsed = SYSUTCDATETIME()
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (TagName, UsageCount, LastUsed)
            VALUES (source.Tag, source.UsageCount, SYSUTCDATETIME());
        
        COMMIT TRANSACTION;
        
        SELECT @@ROWCOUNT as RecordsInserted;
        
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;

-- =====================================================
-- Maintenance procedures para optimización continua
-- =====================================================

CREATE OR ALTER PROCEDURE [dbo].[OptimizeLogEntriesPartitions]
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @CurrentDate DATE = GETDATE();
    DECLARE @PartitionBoundary DATE;
    DECLARE @SQL NVARCHAR(MAX);
    
    -- Reorganize fragmented indexes on current partition
    SET @SQL = N'
    SELECT 
        s.name as SchemaName,
        t.name as TableName, 
        i.name as IndexName,
        ps.avg_fragmentation_in_percent
    FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, NULL) ps
    INNER JOIN sys.tables t ON ps.object_id = t.object_id
    INNER JOIN sys.schemas s ON t.schema_id = s.schema_id  
    INNER JOIN sys.indexes i ON ps.object_id = i.object_id AND ps.index_id = i.index_id
    WHERE s.name = ''dbo'' AND t.name = ''LogEntries''
    AND ps.avg_fragmentation_in_percent > 10
    ORDER BY ps.avg_fragmentation_in_percent DESC;
    ';
    
    EXEC sp_executesql @SQL;
    
    -- Update statistics on main table
    UPDATE STATISTICS [dbo].[LogEntries];
    
    -- Cleanup old partitions (older than 2 years)
    SET @PartitionBoundary = DATEADD(YEAR, -2, @CurrentDate);
    
    PRINT 'Maintenance completed for LogEntries partitions';
END;
```

## Configuración de Azure SQL Managed Instance

### Parámetros de Rendimiento Optimizados

```json
{
  "sqlManagedInstance": {
    "tier": "BusinessCritical",
    "computeGeneration": "Gen5",
    "vCores": 8,
    "storageSize": "2TB",
    "storageAccountType": "Premium_LRS",
    "licenseType": "BasePrice",
    "collation": "SQL_Latin1_General_CP1_CI_AS",
    "publicDataEndpointEnabled": false,
    "proxyOverride": "Proxy",
    "timezoneId": "UTC",
    "instancePoolId": null,
    "maintenanceConfigurationId": "/subscriptions/{subscription-id}/providers/Microsoft.Maintenance/publicMaintenanceConfigurations/SQL_Default",
    "backupStorageRedundancy": "Geo",
    "zoneRedundant": true,
    "administrators": {
      "administratorType": "ActiveDirectory",
      "login": "bitacora-admin-group",
      "sid": "{azure-ad-group-id}",
      "tenantId": "{tenant-id}"
    }
  },
  "databaseConfiguration": {
    "maxDOP": 4,
    "costThresholdForParallelism": 5,
    "maxServerMemory": 6144,
    "optimizeForAdHocWorkloads": true,
    "pageVerify": "CHECKSUM",
    "recoveryModel": "FULL",
    "targetRecoveryTime": 60,
    "maxTransactionLogSize": "200GB",
    "autoGrowthIncrement": "10%",
    "fileGrowthType": "Percent"
  }
}
```

### Configuración de Connection Strings Optimizada

```csharp
// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server={server-name}.{dns-zone}.database.windows.net;Database=BitacoraDB;Authentication=Active Directory Managed Identity;Connection Timeout=30;Command Timeout=120;Application Name=BitacoraAPI;MultipleActiveResultSets=false;Encrypt=true;TrustServerCertificate=false;ConnectRetryCount=3;ConnectRetryInterval=10;",
    "ReadOnlyConnection": "Server={server-name}-readonly.{dns-zone}.database.windows.net;Database=BitacoraDB;Authentication=Active Directory Managed Identity;Connection Timeout=15;Command Timeout=60;Application Name=BitacoraAPI-ReadOnly;MultipleActiveResultSets=false;Encrypt=true;TrustServerCertificate=false;ApplicationIntent=ReadOnly;"
  },
  "DatabaseOptions": {
    "CommandTimeout": 120,
    "MaxRetryCount": 3,
    "MaxRetryDelay": "00:00:30",
    "EnableSensitiveDataLogging": false,
    "EnableServiceProviderCaching": true,
    "EnableDetailedErrors": false,
    "WarningsAsErrors": false,
    "PoolSize": {
      "MinPoolSize": 5,
      "MaxPoolSize": 200
    }
  }
}
```

## Configuración de Azure Service Bus

### Configuración de Colas Optimizada

```json
{
  "serviceBusNamespace": {
    "sku": "Premium",
    "capacity": 2,
    "zoneRedundant": true,
    "queues": [
      {
        "name": "bitacora-high-priority",
        "maxSizeInMegabytes": 5120,
        "messageTimeToLive": "P14D",
        "lockDuration": "PT5M",
        "maxDeliveryCount": 3,
        "deadLetteringOnMessageExpiration": true,
        "duplicateDetectionTimeWindow": "PT10M",
        "enableBatchedOperations": true,
        "enablePartitioning": true,
        "requiresDuplicateDetection": true,
        "enableExpress": false,
        "autoDeleteOnIdle": null,
        "forwardTo": null,
        "forwardDeadLetteredMessagesTo": "bitacora-dlq"
      },
      {
        "name": "bitacora-normal-priority", 
        "maxSizeInMegabytes": 5120,
        "messageTimeToLive": "P14D",
        "lockDuration": "PT5M",
        "maxDeliveryCount": 5,
        "deadLetteringOnMessageExpiration": true,
        "duplicateDetectionTimeWindow": "PT10M",
        "enableBatchedOperations": true,
        "enablePartitioning": true,
        "requiresDuplicateDetection": true,
        "enableExpress": false,
        "autoDeleteOnIdle": null,
        "forwardDeadLetteredMessagesTo": "bitacora-dlq"
      },
      {
        "name": "bitacora-dlq",
        "maxSizeInMegabytes": 1024,
        "messageTimeToLive": "P30D",
        "lockDuration": "PT5M",
        "maxDeliveryCount": 1,
        "deadLetteringOnMessageExpiration": false,
        "enableBatchedOperations": true,
        "enablePartitioning": false,
        "requiresDuplicateDetection": false
      }
    ]
  }
}
```

## Configuración de Redis Cache

### Configuración Optimizada para Rate Limiting y Deduplicación

```json
{
  "redisCache": {
    "sku": "Premium",
    "family": "P",
    "capacity": 3,
    "enableNonSslPort": false,
    "minimumTlsVersion": "1.2",
    "publicNetworkAccess": "Disabled",
    "redisConfiguration": {
      "maxmemory-policy": "allkeys-lru",
      "maxmemory-reserved": 200,
      "maxfragmentationmemory-reserved": 200,
      "maxmemory-delta": 200,
      "notify-keyspace-events": "Ex",
      "aof-backup-enabled": true,
      "aof-storage-connection-string-0": "{storage-connection-string}",
      "rdb-backup-enabled": true,
      "rdb-backup-frequency": "60",
      "rdb-storage-connection-string": "{storage-connection-string}"
    },
    "zones": ["1", "2", "3"]
  },
  "rateLimitingConfig": {
    "defaultLimits": {
      "requestsPerMinute": 1000,
      "requestsPerHour": 50000,
      "requestsPerDay": 1000000
    },
    "premiumLimits": {
      "requestsPerMinute": 5000,
      "requestsPerHour": 250000,
      "requestsPerDay": 5000000
    },
    "keyExpirationSeconds": {
      "rateLimitWindow": 60,
      "deduplicationWindow": 300,
      "sessionCache": 1800
    }
  }
}
```

## Configuración de Monitoreo Avanzado

### Application Insights - Métricas Personalizadas

```csharp
// Configuración de métricas personalizadas
public class BitacoraMetrics
{
    private readonly TelemetryClient _telemetryClient;
    private readonly IMetric _requestsPerSecond;
    private readonly IMetric _queueDepth;
    private readonly IMetric _processingLatency;
    private readonly IMetric _duplicateRate;

    public BitacoraMetrics(TelemetryClient telemetryClient)
    {
        _telemetryClient = telemetryClient;
        
        // Métricas de rendimiento
        _requestsPerSecond = _telemetryClient.GetMetric("Bitacora.RequestsPerSecond");
        _queueDepth = _telemetryClient.GetMetric("Bitacora.QueueDepth");
        _processingLatency = _telemetryClient.GetMetric("Bitacora.ProcessingLatency");
        _duplicateRate = _telemetryClient.GetMetric("Bitacora.DuplicateRate");
    }

    public void TrackRequest(string endpoint, double duration, bool isSuccess)
    {
        _requestsPerSecond.TrackValue(1);
        _processingLatency.TrackValue(duration);
        
        var telemetry = new RequestTelemetry
        {
            Name = endpoint,
            Duration = TimeSpan.FromMilliseconds(duration),
            Success = isSuccess,
            ResponseCode = isSuccess ? "200" : "500"
        };
        
        telemetry.Properties["Endpoint"] = endpoint;
        _telemetryClient.TrackRequest(telemetry);
    }

    public void TrackQueueDepth(int depth)
    {
        _queueDepth.TrackValue(depth);
    }

    public void TrackDuplicate(string correlationId)
    {
        _duplicateRate.TrackValue(1);
        _telemetryClient.TrackEvent("DuplicateDetected", 
            new Dictionary<string, string> { ["CorrelationId"] = correlationId });
    }
}
```

### KQL Queries para Alertas

```kusto
// Alerta: Alta latencia en API (P95 > 500ms)
requests
| where timestamp >= ago(5m)
| where name contains "bitacora"
| summarize 
    P95_Duration = percentile(duration, 95),
    RequestCount = count()
    by bin(timestamp, 1m)
| where P95_Duration > 500
| order by timestamp desc

// Alerta: Profundidad de cola alta (>10,000 mensajes)
customMetrics
| where name == "Bitacora.QueueDepth"
| where timestamp >= ago(5m)
| summarize MaxDepth = max(value) by bin(timestamp, 1m)
| where MaxDepth > 10000
| order by timestamp desc

// Alerta: Alta tasa de errores (>1%)
requests
| where timestamp >= ago(10m)
| where name contains "bitacora"
| summarize 
    TotalRequests = count(),
    FailedRequests = countif(success == false),
    ErrorRate = (countif(success == false) * 100.0) / count()
    by bin(timestamp, 1m)
| where ErrorRate > 1.0
| order by timestamp desc

// Análisis de rendimiento de base de datos
dependencies
| where type == "SQL"
| where timestamp >= ago(30m)
| summarize 
    P50 = percentile(duration, 50),
    P95 = percentile(duration, 95),
    P99 = percentile(duration, 99),
    Count = count()
    by bin(timestamp, 5m), name
| order by timestamp desc
```

## Configuración de Auto-Scaling

### Azure Functions Auto-Scaling

```json
{
  "functionApp": {
    "plan": "Premium",
    "sku": "EP2",
    "preWarmedInstances": 3,
    "maximumElasticWorkerCount": 20,
    "functionAppScaleLimit": 200,
    "scaleSettings": {
      "rules": [
        {
          "metricTrigger": {
            "metricName": "ServiceBusActiveMessageCount",
            "metricResourceUri": "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.ServiceBus/namespaces/{namespace}/queues/bitacora-high-priority",
            "timeGrain": "PT1M",
            "statistic": "Average",
            "timeWindow": "PT5M",
            "timeAggregation": "Average",
            "operator": "GreaterThan",
            "threshold": 1000
          },
          "scaleAction": {
            "direction": "Increase",
            "type": "ChangeCount",
            "value": "2",
            "cooldown": "PT5M"
          }
        }
      ]
    }
  }
}
```

### App Service Auto-Scaling

```json
{
  "appServicePlan": {
    "sku": "P2V3",
    "capacity": 3,
    "autoScaleSettings": {
      "profiles": [
        {
          "name": "DefaultAutoScale",
          "capacity": {
            "minimum": "3",
            "maximum": "10", 
            "default": "3"
          },
          "rules": [
            {
              "metricTrigger": {
                "metricName": "CpuPercentage",
                "timeGrain": "PT1M",
                "statistic": "Average", 
                "timeWindow": "PT5M",
                "timeAggregation": "Average",
                "operator": "GreaterThan",
                "threshold": 70
              },
              "scaleAction": {
                "direction": "Increase",
                "type": "ChangeCount", 
                "value": "2",
                "cooldown": "PT10M"
              }
            },
            {
              "metricTrigger": {
                "metricName": "CpuPercentage",
                "timeGrain": "PT1M",
                "statistic": "Average",
                "timeWindow": "PT15M", 
                "timeAggregation": "Average",
                "operator": "LessThan",
                "threshold": 25
              },
              "scaleAction": {
                "direction": "Decrease",
                "type": "ChangeCount",
                "value": "1", 
                "cooldown": "PT20M"
              }
            }
          ]
        }
      ]
    }
  }
}
```

---

## Estimación de Costos Mensual (USD)

| Componente | SKU/Tier | Cantidad | Costo Mensual |
|------------|----------|----------|---------------|
| **Azure SQL MI** | Business Critical 8 vCore | 1 | $2,920 |
| **Service Bus Premium** | 2 Messaging Units | 1 | $1,340 |
| **Redis Cache Premium** | P3 (26GB) | 1 | $630 |
| **App Service Plan** | P2V3 (3-10 instances) | 1 | $584 - $1,947 |
| **Azure Functions** | Premium EP2 | 1 | $292 - $876 |
| **Application Insights** | 50GB/month | 1 | $287 |
| **Log Analytics** | 50GB/month | 1 | $287 |
| **API Management** | Premium 1 unit | 1 | $2,927 |
| **Load Balancer** | Standard | 1 | $22 |
| **Bandwidth** | Outbound 1TB | 1 | $81 |
| **Storage** | Premium backup | 500GB | $95 |

**Total Estimado: $9,465 - $11,891 USD/mes**

*Nota: Precios pueden variar según región y compromisos de uso. Considerar Reserved Instances para ahorros del 30-60%.*
