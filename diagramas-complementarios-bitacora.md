# Diagramas Complementarios - API de Bitácora

## Diagrama de Deployment y Infraestructura

```mermaid
graph TB
    subgraph "Azure Subscription"
        subgraph "Resource Group: rg-bitacora-prod"
            subgraph "Network - VNet"
                subgraph "Subnet: API (10.0.1.0/24)"
                    APIM[API Management<br/>Premium Tier]
                    ASE[App Service Environment<br/>v3 - Isolated]
                end
                
                subgraph "Subnet: Data (10.0.2.0/24)"
                    SQLMI[SQL Managed Instance<br/>Business Critical]
                    REDIS[Redis Cache Premium]
                end
                
                subgraph "Subnet: Functions (10.0.3.0/24)"
                    FUNC[Azure Functions<br/>Premium Plan]
                end
            end
            
            subgraph "Messaging"
                ASB[Service Bus Premium<br/>Zone Redundant]
            end
            
            subgraph "Monitoring"
                AI[Application Insights]
                LA[Log Analytics]
                KV[Key Vault]
            end
            
            subgraph "Security"
                NSG1[Network Security Group<br/>API Subnet]
                NSG2[Network Security Group<br/>Data Subnet]
                PE[Private Endpoints]
            end
        end
    end

    Internet[Internet] --> APIM
    APIM --> ASE
    ASE --> ASB
    ASE --> REDIS
    ASB --> FUNC
    FUNC --> SQLMI
    
    ASE -.-> AI
    FUNC -.-> AI
    AI --> LA
    
    classDef networkStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef securityStyle fill:#fff8e1,stroke:#f57c00,stroke-width:2px
    classDef dataStyle fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    
    class NSG1,NSG2,PE,KV securityStyle
    class SQLMI,REDIS,ASB dataStyle
```

## Patrón de Procesamiento por Lotes (Batch Processing)

```mermaid
graph LR
    subgraph "Batch Processing Pattern"
        SB[Service Bus Queue] --> BP[Batch Processor<br/>Azure Function]
        BP --> BV[Batch Validator]
        BV --> BT[Batch Transform]
        BT --> BI[Bulk Insert<br/>SQL Batch]
        BI --> BL[Batch Logger]
        
        BP --> DLQ[Dead Letter Queue]
        BV --> ER[Error Reporter]
        ER --> AI[Application Insights]
        
        subgraph "Retry Logic"
            RT[Retry Timer]
            RC[Retry Counter]
            RT --> RC
            RC --> BP
        end
    end
    
    BI --> SQLMI[(SQL Managed<br/>Instance)]
    BL --> LA[Log Analytics]
    
    classDef processStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef errorStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class BP,BV,BT,BI,BL processStyle
    class DLQ,ER,RT,RC errorStyle
```

## Estrategia de Particionamiento de Datos

```mermaid
graph TB
    subgraph "Partitioning Strategy"
        subgraph "Table Partitions by Date"
            P1[Partition 1<br/>2024-01-01 to 2024-01-31<br/>~2.8M records]
            P2[Partition 2<br/>2024-02-01 to 2024-02-28<br/>~2.6M records]
            P3[Partition 3<br/>2024-03-01 to 2024-03-31<br/>~2.8M records]
            P_Current[Current Partition<br/>2024-12-01 to 2024-12-31<br/>Growing...]
        end
        
        subgraph "Archive Strategy"
            ARCH1[Archived 2023<br/>Azure Blob Storage<br/>Cool Tier]
            ARCH2[Archived 2022<br/>Azure Blob Storage<br/>Archive Tier]
        end
        
        subgraph "Index Strategy per Partition"
            IDX1[Clustered: Id<br/>Non-Clustered: EventTimestamp+Tag<br/>Columnstore: Analytics]
        end
    end
    
    P1 --> IDX1
    P2 --> IDX1
    P3 --> IDX1
    P_Current --> IDX1
    
    P1 -.->|After 1 year| ARCH1
    ARCH1 -.->|After 3 years| ARCH2
    
    classDef partitionStyle fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px
    classDef archiveStyle fill:#f9fbe7,stroke:#689f38,stroke-width:2px
    
    class P1,P2,P3,P_Current partitionStyle
    class ARCH1,ARCH2 archiveStyle
```

## Patrón de Circuit Breaker y Resiliencia

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> HalfOpen: Failure threshold reached
    Closed --> Open: Consecutive failures
    
    Open --> HalfOpen: Timeout expired
    HalfOpen --> Closed: Success calls
    HalfOpen --> Open: Failure detected
    
    state Closed {
        [*] --> Monitoring
        Monitoring --> CountingFailures: Request failed
        CountingFailures --> Monitoring: Reset counter
        CountingFailures --> [*]: Threshold reached
    }
    
    state Open {
        [*] --> Rejecting
        Rejecting --> WaitingTimeout: Timer started
        WaitingTimeout --> [*]: Timeout expired
    }
    
    state HalfOpen {
        [*] --> Testing
        Testing --> [*]: Success/Failure
    }
```

## Métricas y KPIs de Monitoreo

```mermaid
graph LR
    subgraph "Performance Metrics"
        TPS[Transactions per Second<br/>Target: 5,000-10,000]
        LAT[API Latency P95<br/>Target: <100ms]
        QD[Queue Depth<br/>Alert: >10,000]
        CPU[CPU Utilization<br/>Alert: >80%]
    end
    
    subgraph "Business Metrics"
        TPD[Total Logs per Day<br/>~8.6M records]
        ERR[Error Rate<br/>Target: <0.1%]
        DUP[Duplicate Rate<br/>Expected: ~5%]
        RET[Retry Rate<br/>Alert: >2%]
    end
    
    subgraph "Infrastructure Metrics"
        MEM[Memory Usage<br/>Alert: >85%]
        DSK[Disk IOPS<br/>Monitor: Peak usage]
        NET[Network Throughput<br/>Monitor: Bandwidth]
        CON[DB Connections<br/>Alert: >80% pool]
    end
    
    subgraph "Alerting Thresholds"
        CRIT[Critical: System Down<br/>P0 - Immediate]
        WARN[Warning: Performance<br/>P1 - 15 minutes]
        INFO[Info: Capacity<br/>P2 - 1 hour]
    end
    
    TPS --> CRIT
    LAT --> WARN
    ERR --> CRIT
    QD --> WARN
    
    classDef performanceStyle fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef businessStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef infraStyle fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef alertStyle fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    
    class TPS,LAT,QD,CPU performanceStyle
    class TPD,ERR,DUP,RET businessStyle
    class MEM,DSK,NET,CON infraStyle
    class CRIT,WARN,INFO alertStyle
```

## Flujo de Escalamiento Automático

```mermaid
flowchart TD
    START[Incoming Load] --> CHECK{Check Current Metrics}
    
    CHECK -->|CPU > 70%| SCALE_OUT[Scale Out API Instances]
    CHECK -->|Queue > 5000| SCALE_FUNC[Scale Function Apps]
    CHECK -->|DTU > 80%| SCALE_DB[Scale Database Tier]
    CHECK -->|Memory > 80%| SCALE_CACHE[Scale Redis Cache]
    
    SCALE_OUT --> WAIT1[Wait 5 minutes]
    SCALE_FUNC --> WAIT2[Wait 3 minutes] 
    SCALE_DB --> WAIT3[Wait 10 minutes]
    SCALE_CACHE --> WAIT4[Wait 5 minutes]
    
    WAIT1 --> VALIDATE1{Metrics Improved?}
    WAIT2 --> VALIDATE2{Queue Reduced?}
    WAIT3 --> VALIDATE3{DTU Normalized?}
    WAIT4 --> VALIDATE4{Cache Hit Improved?}
    
    VALIDATE1 -->|Yes| MONITOR[Continue Monitoring]
    VALIDATE1 -->|No| ALERT1[Alert: Scale Out Failed]
    
    VALIDATE2 -->|Yes| MONITOR
    VALIDATE2 -->|No| ALERT2[Alert: Function Scale Failed]
    
    VALIDATE3 -->|Yes| MONITOR  
    VALIDATE3 -->|No| ALERT3[Alert: DB Scale Failed]
    
    VALIDATE4 -->|Yes| MONITOR
    VALIDATE4 -->|No| ALERT4[Alert: Cache Scale Failed]
    
    MONITOR --> CHECK
    
    ALERT1 --> ESCALATE[Escalate to On-Call]
    ALERT2 --> ESCALATE
    ALERT3 --> ESCALATE  
    ALERT4 --> ESCALATE
    
    classDef checkStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef scaleStyle fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef alertStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class CHECK,VALIDATE1,VALIDATE2,VALIDATE3,VALIDATE4 checkStyle
    class SCALE_OUT,SCALE_FUNC,SCALE_DB,SCALE_CACHE scaleStyle
    class ALERT1,ALERT2,ALERT3,ALERT4,ESCALATE alertStyle
```

## Estrategia de Backup y Disaster Recovery

```mermaid
timeline
    title Backup and Recovery Strategy
    
    section Real-time
        Continuous Backup : SQL MI Point-in-time recovery
                         : Transaction log backup every 5-10 min
                         
    section Daily  
        Full Backup : Automated full backup at 2 AM UTC
                   : Backup retention: 35 days
                   : Cross-region replication
                   
    section Weekly
        Archive Backup : Weekly backup to cool storage
                      : Long-term retention: 2 years
                      
    section Monthly
        DR Testing : Disaster recovery drill
                  : Failover testing to secondary region
                  : RTO: 4 hours, RPO: 1 hour
```

---

## Checklist de Implementación

### Fase 1: Infraestructura Base (Semana 1-2)
- [ ] Crear Resource Groups y VNets
- [ ] Configurar Azure SQL Managed Instance
- [ ] Implementar Azure Service Bus Premium
- [ ] Configurar Redis Cache Premium
- [ ] Establecer conectividad privada (Private Endpoints)

### Fase 2: Aplicación API (Semana 3-4)  
- [ ] Desarrollar API .NET Core con patrones async
- [ ] Implementar middleware de rate limiting
- [ ] Configurar deduplicación con Redis
- [ ] Integrar con Service Bus para encolamiento
- [ ] Implementar health checks y métricas

### Fase 3: Procesamiento Asíncrono (Semana 5-6)
- [ ] Desarrollar Azure Functions para procesamiento
- [ ] Implementar batch processing con retry logic
- [ ] Configurar dead letter queues
- [ ] Optimizar bulk inserts a SQL MI
- [ ] Implementar circuit breaker pattern

### Fase 4: Monitoreo y Observabilidad (Semana 7-8)
- [ ] Configurar Application Insights
- [ ] Crear dashboards en Log Analytics  
- [ ] Implementar alertas proactivas
- [ ] Configurar métricas personalizadas
- [ ] Establecer runbooks de incidentes

### Fase 5: Optimización y Tuning (Semana 9-10)
- [ ] Implementar particionamiento de tablas
- [ ] Optimizar índices y queries
- [ ] Configurar auto-scaling policies  
- [ ] Realizar pruebas de carga
- [ ] Ajustar parámetros de rendimiento

¿Te gustaría que profundice en alguna fase específica o que creemos los scripts de implementación para algún componente?