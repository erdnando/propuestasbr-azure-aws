# Estimación de Costos AWS - Bradescard México

### Flujos adicionales

**Fecha:** 22 de Septiembre, 2025

# **Estimación de Costos**

| Componente                             | Costo (USD)     |
| -------------------------------------- | ---------------- |
| ECS Fargate                            | $798.50          |
| API Gateway                            | $285             |
| Networking                             | $812             |
| Seguridad                              | $625.50          |
| Storage                                | $2               |
| **AWS DevOps**                   | **$312**   |
| Costo mensual                          | **$2,835** |
| **Cliente:** Bradescard México  |                  |
| **Proyecto:** flujos adicionales |                  |

## Resumen Ejecutivo

### Arquitectura Propuesta

- **1 Aplicación Web React** (frontend)
- **APIs .NET Core 8** en contenedores (backend)
- **Amazon ECS con Fargate** para orquestación
- **API Gateway** para gestión de APIs
- **Amazon VPC** con Direct Connect para conectividad segura
- **Seguridad empresarial** con AWS WAF + Network Firewall

### Volúmenes de Transacciones Estimados

| Módulo         | Transacciones/Mes         | Peticiones API/Módulo | Total Peticiones/Mes            |
| --------------- | ------------------------- | ---------------------- | ------------------------------- |
| Módulo 1       | 37,000 - 45,000           | 20                     | 740,000 - 900,000               |
| Módulo 2       | 20,000                    | 20                     | 400,000                         |
| Módulo 3       | 1,000                     | 20                     | 20,000                          |
| Módulo 4       | 20,000                    | 20                     | 400,000                         |
| **TOTAL** | **78,000 - 86,000** | **80**           | **1,560,000 - 1,720,000** |

## Ambientes Propuestos

### Estrategia Recomendada: Accounts por Ambiente

- **DEV** - Desarrollo y pruebas iniciales
- **QA** - Testing y validaciones
- **CERT** - Certificación pre-productiva
- **PROD** - Producción con 200 tiendas

### **Costos con Reserved Instances (4 ambientes)**

| Periodo    | Estrategia                            | Costo Mensual (USD) | Costo Mensual (MXN) | Costo Anual (USD) | Costo Anual (MXN) |
| ---------- | ------------------------------------- | ------------------- | ------------------- | ----------------- | ----------------- |
| Meses 1-12 | Configuración optimizada sin RIs     | 2,835               | 51,030              | 34,020            | 612,360           |
| Mes 13+    | Compra de Reserved Instances (1 año) | 2,480               | 44,640              | 29,760            | 535,680           |

**Nota**: Las Reserved Instances se compran después del primer año de operación, basándose en patrones de uso real validados.

*Tipo de cambio: 1 USD = 18 MXN (septiembre 2025)

## Resumen de Costos por Ambiente

### **Distribución de Gastos por Ambiente**

| Ambiente        | ECS Fargate      | API Gateway      | Networking       | Seguridad        | Storage        | Total (USD)        | Total (MXN)      |
| --------------- | ---------------- | ---------------- | ---------------- | ---------------- | -------------- | ------------------ | ---------------- |
| DEV             | 72.50            | 0.00             | 0.00             | 156.38           | 0.25           | 229.13             | 4,124            |
| QA              | 72.50            | 0.00             | 0.00             | 156.38           | 0.25           | 229.13             | 4,124            |
| CERT            | 72.50            | 0.00             | 0.00             | 156.38           | 0.25           | 229.13             | 4,124            |
| PROD            | 581.00           | 285.00           | 812.00           | 156.36           | 0.50           | 1,834.86           | 33,028           |
| **TOTAL** | **798.50** | **285.00** | **812.00** | **625.50** | **2.00** | **2,523.00** | **45,414** |

### **Notas sobre Distribución de Costos:**

#### **Recursos Compartidos (Asignados a PROD):**

- **API Gateway**: Servicio central que maneja todas las APIs
- **Direct Connect/Networking**: Conectividad principal con on-premise
- **Parte de Seguridad**: AWS Network Firewall protege toda la VPC

#### **Recursos por Ambiente:**

- **ECS Fargate**: Cada ambiente tiene sus propios contenedores
- **Seguridad Distribuida**: CloudWatch, X-Ray, Secrets Manager por ambiente
- **Storage**: Logs y backups específicos por ambiente

### **Beneficios de esta Distribución:**

1. **Control de Presupuesto**: Cada ambiente tiene su costo identificado
2. **Escalabilidad Independiente**: Ajustar recursos por ambiente según necesidad
3. **Justificación de Gastos**: Claridad para stakeholders por área
4. **Optimización Dirigida**: Identificar dónde enfocar ahorros

### **Estrategias de Optimización por Ambiente:**

| Ambiente | Oportunidad de Ahorro  | Estrategia Recomendada                                  |
| -------- | ---------------------- | ------------------------------------------------------- |
| DEV      | Auto-shutdown nocturno | Parar 16hrs/día = 91 USD/mes ahorro                    |
| QA       | Schedule por sprints   | Usar solo durante testing = 115 USD/mes ahorro          |
| CERT     | Uso bajo demanda       | Encender solo para certificaciones = 137 USD/mes ahorro |
| PROD     | Reserved Instances     | RI después del año 1 = 355 USD/mes ahorro             |

# **Estimación de Costos

| Componente                 | Costo Optimizado (USD) |
| -------------------------- | ---------------------- |
| ECS Fargate                | $798.50                |
| API Gateway                | $285                   |
| Networking                 | $812                   |
| Seguridad                  | $625.50                |
| Storage                    | $2                     |
| **TOTAL MESES 1-12** | **$2,523**       |

## Detalle de Costos

### ECS Fargate (Aplicaciones y APIs)

| Componente                                | Configuración                  | Ambiente | Costo Mensual (USD) |
| ----------------------------------------- | ------------------------------- | -------- | ------------------- |
| App React Frontend                        | 0.25 vCPU, 0.5GB RAM, 1-5 tasks | DEV      | $24.50              |
| APIs .NET Core                            | 0.25 vCPU, 0.5GB RAM, 1-5 tasks | DEV      | $48                 |
| App React Frontend                        | 0.25 vCPU, 0.5GB RAM, 1-5 tasks | QA       | $24.50              |
| APIs .NET Core                            | 0.25 vCPU, 0.5GB RAM, 1-5 tasks | QA       | $48                 |
| App React Frontend                        | 0.25 vCPU, 0.5GB RAM, 1-5 tasks | CERT     | $24.50              |
| APIs .NET Core                            | 0.25 vCPU, 0.5GB RAM, 1-5 tasks | CERT     | $48                 |
| App React Frontend                        | 0.5 vCPU, 1GB RAM, 1-5 tasks    | PROD     | $195                |
| APIs .NET Core                            | 0.5 vCPU, 1GB RAM, 1-5 tasks    | PROD     | $386                |
| **Subtotal ECS Fargate Optimizado** |                                 |          | **$798.50**   |

### API Gateway

| Tier                                      | Configuración            | Llamadas Incluidas                   | Costo Mensual (USD) |
| ----------------------------------------- | ------------------------- | ------------------------------------ | ------------------- |
| REST API Standard                         | Multi-región, SLA 99.95% | 1M llamadas gratuitas                | $285                |
| Llamadas adicionales                      | ~600,000 extra            | $3.50 por millón | Incluido en $285 |                     |
| **Subtotal API Gateway Optimizado** |                           |                                      | **$285**      |

### Networking y Conectividad

| Servicio                                 | Configuración Optimizada  | Costo Mensual (USD) |
| ---------------------------------------- | -------------------------- | ------------------- |
| AWS Direct Connect                       | 100 Mbps (escalable a 200) | $585                |
| Amazon VPC                               | Red virtual con subnets    | $65                 |
| VPN Gateway                              | Standard                   | $125                |
| NAT Gateway                              | Multi-AZ                   | $32                 |
| Transferencia de datos                   | 500 GB/mes estimado        | $5                  |
| **Subtotal Networking Optimizado** |                            | **$812**      |

### Seguridad y Monitoreo

| Servicio                     | Configuración        | Costo Mensual (USD) |
| ---------------------------- | --------------------- | ------------------- |
| AWS Network Firewall         | Standard              | $425                |
| AWS WAF                      | Standard              | $35                 |
| AWS Secrets Manager          | 20 secretos           | $18                 |
| Amazon CloudWatch            | 5 GB logs/mes         | $105                |
| AWS X-Ray                    | Tracing distribuido   | $15                 |
| AWS Config                   | Compliance monitoring | $12.50              |
| CloudFormation               | Stack management      | $15                 |
| **Subtotal Seguridad** |                       | **$625.50**   |

### Almacenamiento

| Servicio                   | Configuración | Costo Mensual (USD) |
| -------------------------- | -------------- | ------------------- |
| Amazon S3 (Logs/Backups)   | 10 GB Standard | $2                  |
| **Subtotal Storage** |                | **$2**        |

## -------------------------------------------------------------------------------------

## AWS DevOps - Gestión de Desarrollo y CI/CD

### **Requerimientos del Equipo de Desarrollo**

- **Equipo**: 5-7 desarrolladores
- **Gestión**: User Stories, Tasks con AWS DevOps Guru y Jira integration
- **Código**: Repositorios Git para frontend React y APIs .NET Core
- **CI/CD**: Pipelines automatizados hacia ECR y ECS Fargate
- **Seguimiento**: Sprint management y reporting

### **Costos AWS DevOps**

#### **Licencias de Usuario**

| Tipo de Usuario              | Cantidad             | Costo por Usuario/Mes (USD) | Costo Total Mensual (USD) |
| ---------------------------- | -------------------- | --------------------------- | ------------------------- |
| Atlassian Jira (Team)        | 7 usuarios           | 7.75                        | 54.25                     |
| GitHub Enterprise            | 7 usuarios           | 21.00                       | 147.00                    |
| **Subtotal Licencias** | **7 usuarios** |                             | **201.25**          |

#### **Build Pipelines (CI/CD)**

| Tipo                         | Cantidad    | Especificación                   | Costo Mensual (USD) |
| ---------------------------- | ----------- | --------------------------------- | ------------------- |
| AWS CodeBuild                | 2 projects  | Para React build + .NET Core APIs | 15.00               |
| AWS CodePipeline             | 4 pipelines | Deploy a todos los ambientes      | 4.00                |
| AWS CodeDeploy               | Blue/Green  | Zero-downtime deployments         | 0.00                |
| **Subtotal Pipelines** |             |                                   | **19.00**     |

#### **Amazon ECR (Container Registry)**

| Servicio                    | Configuración    | Propósito                    | Costo Mensual (USD) |
| --------------------------- | ----------------- | ----------------------------- | ------------------- |
| Amazon ECR                  | 500 GB storage    | Imágenes Docker React + APIs | 50.00               |
| Cross-region replication    | 1 replica región | Redundancia para PROD         | $41.75              |
| **Subtotal Registry** |                   |                               | **91.75**     |

#### **AWS Boards y Repos Equivalentes**

| Servicio            | Configuración          | Costo Mensual (USD)           |
| ------------------- | ----------------------- | ----------------------------- |
| GitHub Enterprise   | Unlimited private repos | Incluido en licencias GitHub  |
| Jira                | Unlimited work items    | Incluido en licencias Jira    |
| AWS Systems Manager | Parameter Store         | $0 (hasta 10,000 parámetros) |

### **Resumen de Costos AWS DevOps**

| Componente                 | Costo Mensual (USD) | Costo Mensual (MXN) | Costo Anual (USD) | Costo Anual (MXN) |
| -------------------------- | ------------------- | ------------------- | ----------------- | ----------------- |
| Licencias DevOps           | 201.25              | 3,623               | 2,415             | 43,470            |
| Build Pipelines            | 19.00               | 342                 | 228               | 4,104             |
| Container Registry         | 91.75               | 1,652               | 1,101             | 19,818            |
| **Total AWS DevOps** | **312.00**    | **5,617**     | **3,744**   | **67,392**  |

### **Resumen DevOps**

| Componente           | Costo Mensual (USD) | Costo Mensual (MXN) | Costo Anual (USD) | Costo Anual (MXN) |
| -------------------- | ------------------- | ------------------- | ----------------- | ----------------- |
| **AWS DevOps** | 312                 | 5,617               | 3,744             | 67,392            |

## Comparación de Arquitecturas

### **Mapeo de Servicios Azure vs AWS**

| Categoría               | Azure                | AWS                    | Justificación                     |
| ------------------------ | -------------------- | ---------------------- | ---------------------------------- |
| **Contenedores**   | Container Apps       | ECS Fargate            | Serverless container orchestration |
| **API Management** | API Management       | API Gateway            | API lifecycle management           |
| **Networking**     | ExpressRoute + VNET  | Direct Connect + VPC   | Hybrid connectivity                |
| **Seguridad**      | Firewall + WAF       | Network Firewall + WAF | Enterprise security layers         |
| **Monitoreo**      | Application Insights | CloudWatch + X-Ray     | APM y distributed tracing          |
| **Secretos**       | Key Vault            | Secrets Manager        | Credential management              |
| **CI/CD**          | Azure DevOps         | CodePipeline + GitHub  | DevOps toolchain                   |
| **Registry**       | Container Registry   | ECR                    | Container image storage            |

### **Ventajas por Plataforma**

#### **Azure**

- **DevOps Integrado**: Azure DevOps todo en uno
- **Hybrid Cloud**: Mejor integración con Windows/AD
- **Precio**: Ligeramente más económico ($2,632 vs $2,835)

#### **AWS**

- **Madurez**: Mayor ecosistema de servicios
- **Flexibilidad**: Más opciones de configuración
- **Mercado**: Líder del mercado cloud
- **Third-party**: Mejor integración con herramientas externas

### **Recomendación Técnica**

Para **Bradescard México**, ambas plataformas son viables técnicamente. La decisión debería basarse en:

1. **Experiencia del equipo** con las plataformas
2. **Integración** con sistemas existentes
3. **Políticas corporativas** de la organización
4. **Costos operativos** a largo plazo ($203 USD diferencia mensual)

**Costo Total Comparativo:**

- **Azure**: $2,632 USD/mes
- **AWS**: $2,835 USD/mes
- **Diferencia**: $203 USD/mes (+7.7% AWS)
