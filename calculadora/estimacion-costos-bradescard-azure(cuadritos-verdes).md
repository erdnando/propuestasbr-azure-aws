# Estimación de Costos Azure - Bradescard México (Cuadritos Verdes)

### Flujos adicionales - Backend Only

**Fecha:** 24 de Septiembre, 2025

# **Estimación de Costos**

| Componente                                            |         Costo (USD) |
| ----------------------------------------------------- | ------------------: |
| Container Apps (Backend Only)                         |             $495.00 |
| API Management                                        |             $250.00 |
| Networking                                            |             $765.00 |
| Seguridad                                             |             $584.50 |
| Storage                                               |               $1.00 |
| **Azure DevOps**                                |    **$75.00** |
| **Costo mensual**                               | **$2,170.50** |
| **Cliente:** Bradescard México                 |             México |
| **Proyecto:** flujos adicionales (Backend Only) |    APIs Únicamente |

## Resumen Ejecutivo

### Arquitectura Propuesta - Backend Only

- **APIs .NET Core 8** en contenedores (backend únicamente)
- **Azure Container Apps** para orquestación de APIs
- **API Management** para gestión de APIs
- **Azure VNET** con ExpressRoute para conectividad segura
- **Seguridad empresarial** con Azure Firewall + WAF
- **Sin Frontend** - Solo servicios backend

### Volúmenes de Transacciones Estimados

| Módulo         |         Transacciones/Mes | Peticiones API/Módulo |            Total Peticiones/Mes |
| --------------- | ------------------------: | ---------------------: | ------------------------------: |
| Módulo 1       |           37,000 - 45,000 |                     20 |               740,000 - 900,000 |
| Módulo 2       |                    20,000 |                     20 |                         400,000 |
| Módulo 3       |                     1,000 |                     20 |                          20,000 |
| Módulo 4       |                    20,000 |                     20 |                         400,000 |
| **TOTAL** | **78,000 - 86,000** |           **80** | **1,560,000 - 1,720,000** |

## Ambientes Propuestos

### Estrategia Recomendada: Resource Groups por Ambiente

- **DEV** - Desarrollo y pruebas iniciales
- **QA** - Testing y validaciones
- **CERT** - Certificación pre-productiva
- **PROD** - Producción con 200 tiendas

### **Costos con Reserved Instances (4 ambientes) - Backend Only**

| Periodo    | Estrategia                            |    Costo Mensual (USD) |      Costo Mensual (MXN) | Costo Anual (USD) | Costo Anual (MXN) |
| ---------- | ------------------------------------- | ---------------------: | -----------------------: | ----------------: | ----------------: |
| Meses 1-12 | Configuración optimizada sin RIs     | $2,170.50 | $39,069.00 | $26,046.00 | $468,828.00 |                   |                   |
| Mes 13+    | Compra de Reserved Instances (1 año) | $1,900.94 | $34,216.92 | $22,811.28 | $410,602.56 |                   |                   |

**Nota**: Las Reserved Instances se compran después del primer año de operación, basándose en patrones de uso real validados.

*Tipo de cambio: 1 USD = 18 MXN (septiembre 2025)

## Resumen de Costos por Ambiente - Backend Only

### **Distribución de Gastos por Ambiente**

| Ambiente        |                           Container Apps |                        API Management |                            Networking |            Seguridad | Storage | Total (USD) | Total (MXN) |
| --------------- | ---------------------------------------: | ------------------------------------: | ------------------------------------: | -------------------: | ------: | ----------: | ----------: |
| DEV             |                  $45.00 |          $0.00 |                 $0.00 |       $146.13 |                 $0.25 |       $191.38 |            $3,445.00 |         |             |             |
| QA              |                  $45.00 |          $0.00 |                 $0.00 |       $146.13 |                 $0.25 |       $191.38 |            $3,445.00 |         |             |             |
| CERT            |                  $45.00 |          $0.00 |                 $0.00 |       $146.13 |                 $0.25 |       $191.38 |            $3,445.00 |         |             |             |
| PROD            |                 $360.00 |        $250.00 |               $765.00 |       $146.11 |                 $0.50 |     $1,521.61 |           $27,389.00 |         |             |             |
| **TOTAL** | **$495.00** |    **$250.00** | **$765.00** | **$584.50** | **$1.00** | **$2,095.50** | **$37,719.00** |         |             |             |

### **Notas sobre Distribución de Costos:**

#### **Recursos Compartidos (Asignados a PROD):**

- **API Management**: Servicio central que maneja todas las APIs backend
- **ExpressRoute/Networking**: Conectividad principal con on-premise
- **Parte de Seguridad**: Azure Firewall protege toda la VNET

#### **Recursos por Ambiente:**

- **Container Apps**: Solo APIs .NET Core por ambiente
- **Seguridad Distribuida**: Application Insights, Log Analytics, Key Vault por ambiente
- **Storage**: Logs y backups específicos por ambiente

### **Beneficios de esta Distribución Backend Only:**

1. **Control de Presupuesto**: Cada ambiente tiene su costo identificado
2. **Escalabilidad Independiente**: Ajustar recursos por ambiente según necesidad
3. **Justificación de Gastos**: Claridad para stakeholders por área
4. **Optimización Dirigida**: Identificar dónde enfocar ahorros
5. **Simplicidad Arquitectural**: Solo servicios backend necesarios

### **Estrategias de Optimización por Ambiente - Backend Only:**

| Ambiente |  Oportunidad de Ahorro | Estrategia Recomendada                                   |
| -------- | ---------------------: | -------------------------------------------------------- |
| DEV      | Auto-shutdown nocturno | Parar 16hrs/día = $76 USD/mes ahorro                    |
| QA       |   Schedule por sprints | Usar solo durante testing = $96 USD/mes ahorro           |
| CERT     |       Uso bajo demanda | Encender solo para certificaciones = $115 USD/mes ahorro |
| PROD     |     Reserved Instances | RI después del año 1 = $271 USD/mes ahorro             |

# **Estimación de Costos Backend Only**

| Componente                 | Costo Optimizado (USD) |
| -------------------------- | ---------------------: |
| Container Apps (Backend)   |                $495.00 |
| API Management             |                $250.00 |
| Networking                 |                $765.00 |
| Seguridad                  |                $584.50 |
| Storage                    |                  $1.00 |
| **TOTAL MESES 1-12** |    **$2,095.50** |

## Detalle de Costos

### Container Apps (Solo APIs Backend)

| Componente                                     | Configuración                      | Ambiente        | Costo Mensual (USD) |
| ---------------------------------------------- | ----------------------------------- | --------------- | ------------------: |
| APIs .NET Core (Backend Only)                  | 0.25 vCPU, 0.5GB RAM, 1-5 réplicas | DEV             |              $45.00 |
| APIs .NET Core (Backend Only)                  | 0.25 vCPU, 0.5GB RAM, 1-5 réplicas | QA              |              $45.00 |
| APIs .NET Core (Backend Only)                  | 0.25 vCPU, 0.5GB RAM, 1-5 réplicas | CERT            |              $45.00 |
| APIs .NET Core (Backend Only)                  | 0.5 vCPU, 1GB RAM, 1-5 réplicas    | PROD            |             $360.00 |
| **Subtotal Container Apps Backend Only** | **4 Ambientes**               | **TOTAL** |   **$495.00** |

### API Management

| Tier                                      | Configuración           |      Llamadas Incluidas | Costo Mensual (USD) |
| ----------------------------------------- | ------------------------ | ----------------------: | ------------------: |
| Standard Tier                             | Multi-región, SLA 99.9% |       1.6M llamadas/mes |             $250.00 |
| **Subtotal API Management Backend** | **Tier Standard**  | **1.6M llamadas** |   **$250.00** |

### Networking y Conectividad

| Servicio                              | Configuración Optimizada       | Costo Mensual (USD) |
| ------------------------------------- | ------------------------------- | ------------------: |
| ExpressRoute Standard                 | 100 Mbps (escalable a 200)      |             $520.00 |
| Azure VNET                            | Red virtual con subnets         |              $50.00 |
| VPN Gateway                           | Standard                        |             $150.00 |
| Transferencia de datos                | 500 GB/mes estimado             |              $45.00 |
| **Subtotal Networking Backend** | **Conectividad Híbrida** |   **$765.00** |

### Seguridad y Monitoreo

| Servicio                             | Configuración        | Costo Mensual (USD) |
| ------------------------------------ | --------------------- | ------------------: |
| Azure Firewall                       | Standard              |             $395.00 |
| Web Application Firewall             | Standard              |              $22.00 |
| Azure Key Vault                      | Operaciones estándar |              $15.00 |
| Application Insights                 | 5 GB datos/mes        |             $115.00 |
| Log Analytics                        | 5 GB datos/mes        |              $12.50 |
| Azure Monitor                        | Alertas y métricas   |              $25.00 |
| **Subtotal Seguridad Backend** | **6 Servicios** |   **$584.50** |

### Almacenamiento

| Servicio                           | Configuración          | Costo Mensual (USD) |
| ---------------------------------- | ----------------------- | ------------------: |
| Azure Storage (Logs/Backups)       | 5 GB Standard           |               $1.00 |
| **Subtotal Storage Backend** | **Standard Tier** |     **$1.00** |

## -------------------------------------------------------------------------------------

## Azure DevOps - Gestión de Desarrollo y CI/CD (Backend Only)

### **Requerimientos del Equipo de Desarrollo - Backend Focus**

- **Equipo**: 3-4 desarrolladores backend + 1 lead/QA
- **Gestión**: Stories y Tasks simplificadas con Azure Boards
- **Código**: 1 repositorio Git para APIs .NET Core únicamente
- **CI/CD**: 1 pipeline automatizado hacia Container Registry y Container Apps
- **Seguimiento**: Sprint management simplificado

### **Costos Azure DevOps - Backend Only**

#### **Licencias de Usuario** 

| Tipo de Usuario              |             Cantidad |         Costo por Usuario/Mes (USD) | Costo Total Mensual (USD) |
| ---------------------------- | -------------------: | ----------------------------------: | ------------------------: |
| Basic                        |           3 usuarios |  $6.00 |                     $18.00 |                           |
| Basic + Test Plans           |  1 usuario (Lead/QA) | $52.00 |                     $52.00 |                           |
| **Subtotal Licencias** | **4 usuarios** |                     **Total** |          **$70.00** |

#### **Build Pipelines (CI/CD) - Backend Only**

| Tipo                         |             Cantidad | Especificación                  | Costo Mensual (USD) |
| ---------------------------- | -------------------: | -------------------------------- | ------------------: |
| Microsoft-hosted (Linux)     |       1 parallel job | Para .NET Core APIs (Incluido)   |               $0.00 |
| Self-hosted                  |      0 parallel jobs | No necesario para backend simple |               $0.00 |
| **Subtotal Pipelines** | **1 Pipeline** | **Total**                  |     **$0.00** |

#### **Azure Container Registry - Backend Only**

| Servicio                    | Configuración       | Propósito                   | Costo Mensual (USD) |
| --------------------------- | -------------------- | ---------------------------- | ------------------: |
| Container Registry Basic    | 10 GB storage        | Solo Imágenes Docker APIs   |               $5.00 |
| Sin Geo-replication         | Solo una región     | Simplificado para desarrollo |               $0.00 |
| **Subtotal Registry** | **Basic Tier** | **Total**              |     **$5.00** |

#### **Azure Boards y Repos (Incluido)**

| Servicio         | Configuración          | Costo                          |
| ---------------- | ----------------------- | ------------------------------ |
| Azure Boards     | Unlimited work items    | Incluido en licencias          |
| Azure Repos      | Unlimited private repos | Incluido en licencias          |
| Azure Test Plans | Test case management    | Incluido en Basic + Test Plans |

### **Resumen de Costos Azure DevOps - Backend Only**

| Componente                   |                         Costo Mensual (USD) |                          Costo Mensual (MXN) | Costo Anual (USD) | Costo Anual (MXN) |
| ---------------------------- | ------------------------------------------: | -------------------------------------------: | ----------------: | ----------------: |
| Licencias DevOps             |                 $70.00 |          $1,260.00 |                  $840.00 |        $15,120.00 |                   |                   |
| Build Pipelines              |                  $0.00 |              $0.00 |                    $0.00 |             $0.00 |                   |                   |
| Container Registry           |                   $5.00 |            $90.00 |                   $60.00 |         $1,080.00 |                   |                   |
| **Total Azure DevOps** | **$75.00** |      **$1,350.00** | **$900.00** |     **$16,200.00** |                   |                   |

### **Resumen DevOps Backend Only**

| Componente             |       Costo Mensual (USD) |         Costo Mensual (MXN) | Costo Anual (USD) | Costo Anual (MXN) |
| ---------------------- | ------------------------: | --------------------------: | ----------------: | ----------------: |
| **Azure DevOps** | $75.00 |        $1,350.00 | $900.00 |        $16,200.00 |                   |                   |

## **Comparación: Propuesta Original vs Backend Only**

| Componente              |                                  Original (USD) |  Backend Only (USD) |    Ahorro (USD) | % Ahorro |
| ----------------------- | ----------------------------------------------: | ------------------: | --------------: | -------: |
| Container Apps          |                     $742.50 |           $495.00 |             $247.50 |           33.3% |          |
| API Management          |                     $250.00 |           $250.00 |               $0.00 |              0% |          |
| Networking              |                     $765.00 |           $765.00 |               $0.00 |              0% |          |
| Seguridad               |                     $584.50 |           $584.50 |               $0.00 |              0% |          |
| Storage                 |                       $1.00 |             $1.00 |               $0.00 |              0% |          |
| Azure DevOps            |                     $289.00 |            $75.00 |             $214.00 |           74.0% |          |
| **TOTAL MENSUAL** |  **$2,632.00** |      **$2,170.50** |   **$461.50** | **17.5%** |          |
| **TOTAL ANUAL**   | **$31,584.00** |     **$26,046.00** | **$5,538.00** | **17.5%** |          |

### **Beneficios de la Versión Backend Only:**

1. **Ahorro Significativo**: $461.50 USD/mes ($5,538.00 USD/año)
2. **Menor Complejidad**: Solo gestionar servicios backend
3. **Deployment Simplificado**: Un solo pipeline de CI/CD
4. **Mantenimiento Reducido**: Menos componentes que monitorear
5. **Escalabilidad Focalizada**: Optimización específica para APIs

### **Consideraciones Importantes:**

- **Frontend Externo**: El cliente deberá implementar el frontend por separado
- **CORS Configuration**: APIs deben configurarse para permitir llamadas desde frontend externo
- **API Documentation**: Mayor importancia en documentación de APIs (Swagger/OpenAPI)
- **Security**: Configuración robusta de autenticación y autorización en APIs

### **Recomendaciones de Implementación:**

1. **Fase 1**: Implementar solo ambiente DEV + PROD
2. **Fase 2**: Agregar QA y CERT según necesidades
3. **Optimización**: Reserved Instances después de 6 meses de uso
4. **Monitoreo**: Implementar alertas proactivas para APIs
