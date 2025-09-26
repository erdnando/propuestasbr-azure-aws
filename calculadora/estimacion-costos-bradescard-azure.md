# Estimación de Costos Azure - Bradescard México

### Flujos adicionales

**Fecha:** 22 de Septiembre, 2025

# **Estimación de Costos**

| Componente                             | Costo (USD)     |
| -------------------------------------- | ---------------- |
| Container Apps                         | $742.50          |
| API Management                         | $250             |
| Networking                             | $765             |
| Seguridad                              | $584.50          |
| Storage                                | $1               |
| **Azure DevOps**                 | **$289**   |
| **Costo mensual**                | **$2,632** |
| **Cliente:** Bradescard México  |                  |
| **Proyecto:** flujos adicionales |                  |

## Resumen Ejecutivo

### Arquitectura Propuesta

- **1 Aplicación Web React** (frontend)
- **APIs .NET Core 8** en contenedores (backend)
- **Azure Container Apps** para orquestación
- **API Management** para gestión de APIs
- **Azure VNET** con ExpressRoute para conectividad segura
- **Seguridad empresarial** con Azure Firewall + WAF

### Volúmenes de Transacciones Estimados

| Módulo         | Transacciones/Mes         | Peticiones API/Módulo | Total Peticiones/Mes            |
| --------------- | ------------------------- | ---------------------- | ------------------------------- |
| Módulo 1       | 37,000 - 45,000           | 20                     | 740,000 - 900,000               |
| Módulo 2       | 20,000                    | 20                     | 400,000                         |
| Módulo 3       | 1,000                     | 20                     | 20,000                          |
| Módulo 4       | 20,000                    | 20                     | 400,000                         |
| **TOTAL** | **78,000 - 86,000** | **80**           | **1,560,000 - 1,720,000** |

## Ambientes Propuestos

### Estrategia Recomendada: Resource Groups por Ambiente

- **DEV** - Desarrollo y pruebas iniciales
- **QA** - Testing y validaciones
- **CERT** - Certificación pre-productiva
- **PROD** - Producción con 200 tiendas

### **Costos con Reserved Instances (4 ambientes)**

| Periodo    | Estrategia                            | Costo Mensual (USD) | Costo Mensual (MXN) | Costo Anual (USD) | Costo Anual (MXN) |
| ---------- | ------------------------------------- | ------------------- | ------------------- | ----------------- | ----------------- |
| Meses 1-12 | Configuración optimizada sin RIs     | 2,632               | 47,376              | 31,584            | 568,512           |
| Mes 13+    | Compra de Reserved Instances (1 año) | 2,301               | 41,418              | 27,612            | 497,016           |

**Nota**: Las Reserved Instances se compran después del primer año de operación, basándose en patrones de uso real validados.

*Tipo de cambio: 1 USD = 18 MXN (septiembre 2025)

## Resumen de Costos por Ambiente

### **Distribución de Gastos por Ambiente**

| Ambiente        | Container Apps   | API Management   | Networking       | Seguridad        | Storage        | Total (USD)        | Total (MXN)      |
| --------------- | ---------------- | ---------------- | ---------------- | ---------------- | -------------- | ------------------ | ---------------- |
| DEV             | 67.50            | 0.00             | 0.00             | 146.13           | 0.25           | 213.88             | 3,850            |
| QA              | 67.50            | 0.00             | 0.00             | 146.13           | 0.25           | 213.88             | 3,850            |
| CERT            | 67.50            | 0.00             | 0.00             | 146.13           | 0.25           | 213.88             | 3,850            |
| PROD            | 540.00           | 250.00           | 765.00           | 146.11           | 0.50           | 1,701.61           | 30,629           |
| **TOTAL** | **742.50** | **250.00** | **765.00** | **584.50** | **1.00** | **2,343.00** | **42,174** |

### **Notas sobre Distribución de Costos:**

#### **Recursos Compartidos (Asignados a PROD):**

- **API Management**: Servicio central que maneja todas las APIs
- **ExpressRoute/Networking**: Conectividad principal con on-premise
- **Parte de Seguridad**: Azure Firewall protege toda la VNET

#### **Recursos por Ambiente:**

- **Container Apps**: Cada ambiente tiene sus propios contenedores
- **Seguridad Distribuida**: Application Insights, Log Analytics, Key Vault por ambiente
- **Storage**: Logs y backups específicos por ambiente

### **Beneficios de esta Distribución:**

1. **Control de Presupuesto**: Cada ambiente tiene su costo identificado
2. **Escalabilidad Independiente**: Ajustar recursos por ambiente según necesidad
3. **Justificación de Gastos**: Claridad para stakeholders por área
4. **Optimización Dirigida**: Identificar dónde enfocar ahorros

### **Estrategias de Optimización por Ambiente:**

| Ambiente | Oportunidad de Ahorro  | Estrategia Recomendada                                  |
| -------- | ---------------------- | ------------------------------------------------------- |
| DEV      | Auto-shutdown nocturno | Parar 16hrs/día = 85 USD/mes ahorro                    |
| QA       | Schedule por sprints   | Usar solo durante testing = 107 USD/mes ahorro          |
| CERT     | Uso bajo demanda       | Encender solo para certificaciones = 128 USD/mes ahorro |
| PROD     | Reserved Instances     | RI después del año 1 = 331 USD/mes ahorro             |

# **Estimación de Costos

| Componente                 | Costo Optimizado (USD) |
| -------------------------- | ---------------------- |
| Container Apps             | $742.50                |
| API Management             | $250                   |
| Networking                 | $765                   |
| Seguridad                  | $584.50                |
| Storage                    | $1                     |
| **TOTAL MESES 1-12** | **$2,343**       |

## Detalle de Costos

### Container Apps (Aplicaciones y APIs)

| Componente                                   | Configuración                      | Ambiente | Costo Mensual (USD) |
| -------------------------------------------- | ----------------------------------- | -------- | ------------------- |
| App React Frontend                           | 0.25 vCPU, 0.5GB RAM, 1-5 réplicas | DEV      | $22.50              |
| APIs .NET Core                               | 0.25 vCPU, 0.5GB RAM, 1-5 réplicas | DEV      | $45                 |
| App React Frontend                           | 0.25 vCPU, 0.5GB RAM, 1-5 réplicas | QA       | $22.50              |
| APIs .NET Core                               | 0.25 vCPU, 0.5GB RAM, 1-5 réplicas | QA       | $45                 |
| App React Frontend                           | 0.25 vCPU, 0.5GB RAM, 1-5 réplicas | CERT     | $22.50              |
| APIs .NET Core                               | 0.25 vCPU, 0.5GB RAM, 1-5 réplicas | CERT     | $45                 |
| App React Frontend                           | 0.5 vCPU, 1GB RAM, 1-5 réplicas    | PROD     | $180                |
| APIs .NET Core                               | 0.5 vCPU, 1GB RAM, 1-5 réplicas    | PROD     | $360                |
| **Subtotal Container Apps Optimizado** |                                     |          | **$742.50**   |

### API Management

| Tier                                         | Configuración           | Llamadas Incluidas     | Costo Mensual (USD) |
| -------------------------------------------- | ------------------------ | ---------------------- | ------------------- |
| Standard (Mes 7+)                            | Multi-región, SLA 99.9% | 1M llamadas            | $250                |
| Llamadas adicionales                         | ~600,000 extra           | $0.60 por 1,000 | $360 |                     |
| **Subtotal API Management Optimizado** |                          |                        | **$250**      |

### Networking y Conectividad

| Servicio                                 | Configuración Optimizada  | Costo Mensual (USD) |
| ---------------------------------------- | -------------------------- | ------------------- |
| ExpressRoute Standard                    | 100 Mbps (escalable a 200) | $520                |
| Azure VNET                               | Red virtual con subnets    | $50                 |
| VPN Gateway                              | Standard                   | $150                |
| Transferencia de datos                   | 500 GB/mes estimado        | $45                 |
| **Subtotal Networking Optimizado** |                            | **$765**      |

### Seguridad y Monitoreo

| Servicio                     | Configuración        | Costo Mensual (USD) |
| ---------------------------- | --------------------- | ------------------- |
| Azure Firewall               | Standard              | $395                |
| Web Application Firewall     | Standard              | $22                 |
| Azure Key Vault              | Operaciones estándar | $15                 |
| Application Insights         | 5 GB datos/mes        | $115                |
| Log Analytics                | 5 GB datos/mes        | $12.50              |
| Azure Monitor                | Alertas y métricas   | $25                 |
| **Subtotal Seguridad** |                       | **$584.50**   |

### Almacenamiento

| Servicio                     | Configuración | Costo Mensual (USD) |
| ---------------------------- | -------------- | ------------------- |
| Azure Storage (Logs/Backups) | 5 GB Standard  | $1                  |
| **Subtotal Storage**   |                | **$1**        |

## -------------------------------------------------------------------------------------

## Azure DevOps - Gestión de Desarrollo y CI/CD

### **Requerimientos del Equipo de Desarrollo**

- **Equipo**: 5-7 desarrolladores
- **Gestión**: Épicas, Stories, Tasks con Azure Boards
- **Código**: Repositorios Git para frontend React y APIs .NET Core
- **CI/CD**: Pipelines automatizados hacia Container Registry y Container Apps
- **Seguimiento**: Sprint management y reporting

### **Costos Azure DevOps**

#### **Licencias de Usuario**

| Tipo de Usuario              | Cantidad              | Costo por Usuario/Mes (USD) | Costo Total Mensual (USD) |
| ---------------------------- | --------------------- | --------------------------- | ------------------------- |
| Basic                        | 5 usuarios            | 6.00                        | 30.00                     |
| Basic + Test Plans           | 2 usuarios (Leads/QA) | 52.00                       | 104.00                    |
| **Subtotal Licencias** | **7 usuarios**  |                             | **134.00**          |

#### **Build Pipelines (CI/CD)**

| Tipo                         | Cantidad        | Especificación                   | Costo Mensual (USD) |
| ---------------------------- | --------------- | --------------------------------- | ------------------- |
| Microsoft-hosted (Linux)     | 2 parallel jobs | Para React build + .NET Core APIs | 80.00               |
| Self-hosted                  | 1 parallel job  | Para deployment a Container Apps  | 0.00                |
| **Subtotal Pipelines** |                 |                                   | **80.00**     |

#### **Azure Container Registry**

| Servicio                    | Configuración    | Propósito                    | Costo Mensual (USD) |
| --------------------------- | ----------------- | ----------------------------- | ------------------- |
| Container Registry Premium  | 500 GB storage    | Imágenes Docker React + APIs | 50.00               |
| Geo-replication             | 1 replica región | Redundancia para PROD         | 25.00               |
| **Subtotal Registry** |                   |                               | **75.00**     |

#### **Azure Boards y Repos (Incluido)**

| Servicio         | Configuración          | Costo                          |
| ---------------- | ----------------------- | ------------------------------ |
| Azure Boards     | Unlimited work items    | Incluido en licencias          |
| Azure Repos      | Unlimited private repos | Incluido en licencias          |
| Azure Test Plans | Test case management    | Incluido en Basic + Test Plans |

### **Resumen de Costos Azure DevOps**

| Componente                   | Costo Mensual (USD) | Costo Mensual (MXN) | Costo Anual (USD) | Costo Anual (MXN) |
| ---------------------------- | ------------------- | ------------------- | ----------------- | ----------------- |
| Licencias DevOps             | 134.00              | 2,412               | 1,608             | 28,944            |
| Build Pipelines              | 80.00               | 1,440               | 960               | 17,280            |
| Container Registry           | 75.00               | 1,350               | 900               | 16,200            |
| **Total Azure DevOps** | **289.00**    | **5,202**     | **3,468**   | **62,424**  |

### **Resumen DevOps**

| Componente             | Costo Mensual (USD) | Costo Mensual (MXN) | Costo Anual (USD) | Costo Anual (MXN) |
| ---------------------- | ------------------- | ------------------- | ----------------- | ----------------- |
| **Azure DevOps** | 289                 | 5,202               | 3,468             | 62,424            |
