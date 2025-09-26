# Arquitectura API de Bitácora de Alto Rendimiento

## Visión General
Esta arquitectura está diseñada para manejar miles de transacciones por segundo para una API de bitácora, implementando patrones de encolamiento, procesamiento asíncrono y optimizaciones de base de datos.

## Diagrama Principal de Arquitectura

```mermaid
graph TB
    %% Capa de Entrada
    subgraph "Capa de Entrada"
        LB[Azure Load Balancer<br/>Standard SKU]
        APIM[Azure API Management<br/>Premium Tier]
    end

    %% Capa de API
    subgraph "Capa de Aplicación"
        API1[API .NET Core 8<br/>Instance 1]
        API2[API .NET Core 8<br/>Instance 2]
        API3[API .NET Core 8<br/>Instance N]
    end

    %% Capa de Encolamiento
    subgraph "Capa de Messaging"
        ASB[Azure Service Bus<br/>Premium Tier<br/>Partitioned Queues]
        REDIS[Azure Cache for Redis<br/>Premium P3<br/>Rate Limiting & Dedup]
    end

    %% Capa de Procesamiento
    subgraph "Capa de Procesamiento"
        AF1[Azure Function<br/>Consumption Plan<br/>Processor 1]
        AF2[Azure Function<br/>Premium Plan<br/>Processor 2]
        AF3[Azure Function<br/>Dedicated Plan<br/>Batch Processor]
    end

    %% Capa de Datos
    subgraph "Capa de Persistencia"
        SQLMI[Azure SQL Managed Instance<br/>Business Critical<br/>Multi-Zone]
        COSMOS[Azure Cosmos DB<br/>Hot Path Analytics<br/>Change Feed]
    end

    %% Monitoreo y Observabilidad
    subgraph "Observabilidad"
        AI[Application Insights<br/>Custom Metrics]
        LA[Log Analytics<br/>KQL Queries]
        GRAF[Grafana Dashboard<br/>Real-time Monitoring]
    end

    %% Flujo de datos
    Client[Cliente/Aplicación] --> LB
    LB --> APIM
    APIM --> API1
    APIM --> API2
    APIM --> API3
    
    API1 --> REDIS
    API2 --> REDIS
    API3 --> REDIS
    
    API1 --> ASB
    API2 --> ASB
    API3 --> ASB
    
    ASB --> AF1
    ASB --> AF2
    ASB --> AF3
    
    AF1 --> SQLMI
    AF2 --> SQLMI
    AF3 --> SQLMI
    
    AF1 --> COSMOS
    AF2 --> COSMOS
    
    API1 --> AI
    API2 --> AI
    API3 --> AI
    AF1 --> AI
    AF2 --> AI
    AF3 --> AI
    
    AI --> LA
    LA --> GRAF

    %% Estilos
    classDef apiStyle fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef queueStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef dbStyle fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef monitorStyle fill:#fff3e0,stroke:#f57c00,stroke-width:2px

    class API1,API2,API3 apiStyle
    class ASB,REDIS queueStyle
    class SQLMI,COSMOS dbStyle
    class AI,LA,GRAF monitorStyle
```

## Diagrama de Flujo de Datos Detallado

```mermaid
sequenceDiagram
    participant C as Cliente
    participant APIM as API Management
    participant API as API .NET Core
    participant R as Redis Cache
    participant SB as Service Bus
    participant AF as Azure Function
    participant DB as SQL MI
    participant AI as App Insights

    C->>APIM: POST /api/logs<br/>{timestamp, tag, description}
    APIM->>APIM: Rate Limiting<br/>Authentication<br/>Validation
    APIM->>API: Forward Request
    
    API->>R: Check Deduplication<br/>Key: hash(payload)
    R-->>API: Cache Miss/Hit
    
    alt Cache Miss (New Entry)
        API->>R: Store Dedup Key<br/>TTL: 5 minutes
        API->>SB: Enqueue Message<br/>Partition by DateTime
        API-->>APIM: 202 Accepted<br/>{id, status}
        APIM-->>C: 202 Accepted
        
        SB->>AF: Trigger Processing<br/>Batch Size: 100
        AF->>AF: Validate & Transform
        AF->>DB: Bulk Insert<br/>Batch Operations
        AF->>AI: Log Metrics<br/>Success/Failure
        
    else Cache Hit (Duplicate)
        API-->>APIM: 409 Duplicate
        APIM-->>C: 409 Duplicate
    end

    Note over AF,DB: Retry Logic<br/>Dead Letter Queue<br/>Error Handling
```

## Esquema de Base de Datos Optimizado

```mermaid
erDiagram
    LOG_ENTRIES {
        bigint Id PK "Identity, Clustered Index"
        datetime2 EventTimestamp "Non-null, Indexed"
        nvarchar_50 Tag "Non-null, Indexed"
        nvarchar_max Description "Nullable"
        datetime2 CreatedAt "Default: GETUTCDATE()"
        uniqueidentifier CorrelationId "For tracking"
        tinyint ProcessingStatus "0=Pending,1=Processed,2=Failed"
        int RetryCount "Default: 0"
    }
    
    LOG_PARTITIONS {
        int PartitionId PK
        date PartitionDate
        bigint MinId
        bigint MaxId
        varchar_20 Status
    }
    
    LOG_TAGS {
        int TagId PK "Identity"
        nvarchar_50 TagName "Unique"
        datetime2 CreatedAt
        bit IsActive
    }
    
    LOG_ENTRIES ||--o{ LOG_TAGS : "FK_Tag"
    LOG_PARTITIONS ||--o{ LOG_ENTRIES : "Partitioned_By_Date"
```

## Componentes Clave y Mejoras Arquitectónicas

### 1. **API Gateway y Load Balancing**
- **Azure API Management**: Throttling, authentication, caching
- **Azure Load Balancer**: Distribución de carga con health checks
- **Rate Limiting**: 10,000 requests/minute por cliente

### 2. **Encolamiento y Procesamiento Asíncrono**
- **Azure Service Bus Premium**: 
  - Partitioned queues para mayor throughput
  - Dead letter queues para manejo de errores
  - Duplicate detection habilitada
- **Redis Cache**: Deduplicación y rate limiting en memoria

### 3. **Optimizaciones de Base de Datos**
```sql
-- Índices optimizados para consultas frecuentes
CREATE CLUSTERED INDEX IX_LogEntries_Id ON LogEntries(Id)
CREATE NONCLUSTERED INDEX IX_LogEntries_EventTimestamp_Tag 
    ON LogEntries(EventTimestamp DESC, Tag) 
    INCLUDE (Description, CorrelationId)

-- Particionamiento por fecha para mejor rendimiento
CREATE PARTITION SCHEME PS_LogEntries_Date 
    AS PARTITION PF_LogEntries_Date TO ([PRIMARY], [PARTITION_2024_01], [PARTITION_2024_02], ...)
```

### 4. **Escalabilidad y Rendimiento**
- **Auto-scaling**: Basado en métricas de CPU, memoria y cola
- **Connection pooling**: Optimizado para .NET Core
- **Bulk operations**: Inserts en lotes de 100-1000 registros
- **Read replicas**: Para consultas de reporting

### 5. **Monitoreo y Observabilidad**
- **Application Insights**: Métricas personalizadas, trazabilidad
- **KQL Queries**: Alertas proactivas y dashboards
- **Health checks**: Endpoints para validar estado de servicios

## Especificaciones Técnicas Recomendadas

### Azure SQL Managed Instance
- **Tier**: Business Critical (4-8 vCores)
- **Storage**: 1TB Premium SSD con auto-growth
- **Backup**: Automated backups con 7-day retention
- **Security**: Always Encrypted para datos sensibles

### Azure Service Bus
- **Tier**: Premium (1-8 Messaging Units)
- **Features**: Partitioning, Duplicate Detection, Dead Letter Queues
- **Message TTL**: 14 days
- **Max message size**: 1MB

### Azure Functions
- **Plan**: Premium EP2 para procesamiento intensivo
- **Runtime**: .NET 8 Isolated
- **Concurrency**: Max 200 per instance
- **Timeout**: 30 minutes para batch processing

## Estimación de Capacidad

| Métrica | Valor |
|---------|-------|
| **Requests/segundo** | 5,000-10,000 |
| **Messages en cola** | 100,000 (pico) |
| **Latencia API** | <100ms (p95) |
| **Throughput BD** | 50,000 inserts/min |
| **Retención datos** | 2 años (particionado) |
| **Availability** | 99.95% SLA |

## Consideraciones de Seguridad

1. **Authentication**: Azure AD + JWT tokens
2. **Authorization**: RBAC granular por operación  
3. **Network**: VNet integration, Private Endpoints
4. **Data**: Encryption at rest y in transit
5. **Monitoring**: Security alerts y audit logs

---

**Próximos pasos**: ¿Te gustaría que detalle algún componente específico o que creemos diagramas adicionales para el deployment o la implementación del código?