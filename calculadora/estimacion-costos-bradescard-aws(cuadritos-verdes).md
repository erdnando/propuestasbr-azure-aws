# Estimación de Costos AWS - Bradescard México (Backend Only)

### Flujos adicionales - Versión Optimizada Sin Frontend

**Fecha:** 24 de Septiembre, 2025

# **Estimación de Costos - Backend Only**

| Componente                                            | Costo (USD)         |
| ----------------------------------------------------- | ------------------- |
| ECS Fargate                                           | $515.04             |
| API Gateway                                           | $285.00             |
| Networking                                            | $812.00             |
| Seguridad                                             | $625.50             |
| Storage                                               | $2.00               |
| **AWS DevOps**                                  | **$102.00**   |
| **Costo mensual**                               | **$2,341.54** |
| **Cliente:** Bradescard México                 |                     |
| **Proyecto:** flujos adicionales (Backend Only) |                     |

## Resumen Ejecutivo - Backend Only

### Arquitectura Propuesta (Sin Frontend)

- **APIs .NET Core 8** en contenedores (backend únicamente)
- **Amazon ECS con Fargate** para orquestación de contenedores
- **API Gateway** para gestión y exposición de APIs
- **Amazon VPC** con Direct Connect para conectividad híbrida segura
- **Seguridad empresarial** con AWS WAF + Network Firewall + Shield
- **No incluye:** Aplicación Web React (frontend será responsabilidad del cliente)

### Volúmenes de Transacciones Estimados

| Módulo         |         Transacciones/Mes | Peticiones API/Módulo |            Total Peticiones/Mes |
| --------------- | ------------------------: | ---------------------: | ------------------------------: |
| Módulo 1       |           37,000 - 45,000 |                     20 |               740,000 - 900,000 |
| Módulo 2       |                    20,000 |                     20 |                         400,000 |
| Módulo 3       |                     1,000 |                     20 |                          20,000 |
| Módulo 4       |                    20,000 |                     20 |                         400,000 |
| **TOTAL** | **78,000 - 86,000** |           **80** | **1,560,000 - 1,720,000** |

## Ambientes Propuestos

### Estrategia Recomendada: Accounts por Ambiente

- **DEV** - Desarrollo y pruebas de APIs
- **QA** - Testing y validaciones de APIs
- **CERT** - Certificación pre-productiva de APIs
- **PROD** - Producción con 200 tiendas

### **Costos con Reserved Instances (4 ambientes) - Backend Only**

| Periodo    | Estrategia                            |    Costo Mensual (USD) |      Costo Mensual (MXN) | Costo Anual (USD) | Costo Anual (MXN) |
| ---------- | ------------------------------------- | ---------------------: | -----------------------: | ----------------: | ----------------: |
| Meses 1-12 | Configuración optimizada sin RIs | $2,341.54 | $42,147.72 | $28,098.48 | $505,772.64 |
| Mes 13+ | Compra de Reserved Instances (1 año) | $2,060.55 | $37,089.90 | $24,726.60 | $445,078.80 |

**Nota**: Las Reserved Instances se compran después del primer año de operación, basándose en patrones de uso real validados.

*Tipo de cambio: 1 USD = 18 MXN (septiembre 2025)

## Resumen de Costos por Ambiente - Backend Only

### **Distribución de Gastos por Ambiente**

| Ambiente | ECS Fargate | API Gateway | Networking | Seguridad | Storage | AWS DevOps | Total (USD) | Total (MXN) |
|----------|------------:|------------:|-----------:|----------:|--------:|-----------:|------------:|------------:|
| DEV | $53.28 | $0.00 | $0.00 | $156.38 | $0.25 | $25.50 | $235.41 | $4,237.38 |
| QA | $53.28 | $0.00 | $0.00 | $156.38 | $0.25 | $25.50 | $235.41 | $4,237.38 |
| CERT | $53.28 | $0.00 | $0.00 | $156.38 | $0.25 | $25.50 | $235.41 | $4,237.38 |
| PROD | $355.20 | $285.00 | $812.00 | $156.36 | $1.25 | $25.50 | $1,635.31 | $29,435.58 |
| **TOTAL** | **$515.04** | **$285.00** | **$812.00** | **$625.50** | **$2.00** | **$102.00** | **$2,341.54** | **$42,147.72** |

### **Notas sobre Distribución de Costos:**

1. **ECS Fargate**: Escalado según demanda por ambiente
2. **API Gateway**: Solo PROD maneja tráfico real de 200 tiendas
3. **Networking**: Direct Connect compartido, asignado solo a PROD
4. **Seguridad**: WAF distribuido equitativamente entre ambientes
5. **Storage**: S3 y RDS proporcional al uso por ambiente

## Detalle de Costos por Servicio - Backend Only

### **1. Amazon ECS Fargate - Backend Only**

| Ambiente | vCPU | RAM (GB) | Horas/Mes | Costo por Contenedor | Contenedores | Total (USD) |
|----------|-----:|---------:|----------:|--------------------:|-------------:|------------:|
| DEV | 1 | 2 | 730 | $35.52 | 1 | $35.52 |
| DEV (API2) | 0.5 | 1 | 730 | $17.76 | 1 | $17.76 |
| QA | 1 | 2 | 730 | $35.52 | 1 | $35.52 |
| QA (API2) | 0.5 | 1 | 730 | $17.76 | 1 | $17.76 |
| CERT | 1 | 2 | 730 | $35.52 | 1 | $35.52 |
| CERT (API2) | 0.5 | 1 | 730 | $17.76 | 1 | $17.76 |
| PROD | 2 | 4 | 730 | $71.04 | 3 | $213.12 |
| PROD (API2) | 2 | 4 | 730 | $71.04 | 2 | $142.08 |
| **Subtotal ECS Fargate Backend Only** | **9 vCPU** | **18 GB** | **TOTAL** | **8 Tipos de Contenedor** | **11 Instancias** | **$515.04** |

### **2. Amazon API Gateway - Backend Only**

| Componente                             | Especificación         |                        Cantidad Mensual | Costo Mensual (USD) |
| -------------------------------------- | ----------------------- | --------------------------------------: | ------------------: |
| REST API Calls                         | Primeros 333M           |                               1,600,000 |               $5.60 |
| Llamadas adicionales                   | ~600,000 extra          | $3.50 por millón  |              $2.10 |                     |
| Data Transfer Out                      | 50 GB                   |  $0.09 por GB      |              $4.50 |                     |
| CloudWatch Logs                        | Logs detallados         |                                   10 GB |               $5.00 |
| **Subtotal API Gateway Backend** | **1.6M llamadas** |                         **TOTAL** |   **$285.00** |

### **3. Networking - Backend Only**

| Servicio                              | Especificación                 | Costo Mensual (USD) |
| ------------------------------------- | ------------------------------- | ------------------: |
| Direct Connect (1 Gbps)               | Conectividad híbrida           |             $216.00 |
| VPC Endpoints                         | S3, ECR, CloudWatch             |              $65.70 |
| NAT Gateway                           | 3 AZs                           |             $135.00 |
| Elastic Load Balancer                 | Application Load Balancer       |              $22.50 |
| Route 53                              | DNS privado                     |              $18.00 |
| Transit Gateway                       | Conectividad entre VPCs         |              $36.00 |
| Data Transfer                         | Entre servicios                 |             $318.80 |
| **Subtotal Networking Backend** | **Conectividad Híbrida** |   **$812.00** |

### **4. Seguridad - Backend Only**

| Servicio                             | Especificación          | Costo Mensual (USD) |
| ------------------------------------ | ------------------------ | ------------------: |
| AWS WAF                              | Web Application Firewall |              $85.00 |
| AWS Shield Advanced                  | DDoS Protection          |           $3,000.00 |
| AWS Network Firewall                 | Firewall de red          |             $385.00 |
| AWS Secrets Manager                  | Gestión de secretos     |              $12.00 |
| AWS Certificate Manager              | Certificados SSL         |               $0.00 |
| AWS GuardDuty                        | Threat detection         |              $18.50 |
| AWS Security Hub                     | Security posture         |              $25.00 |
| **Subtotal Seguridad Backend** | **7 Servicios**    |   **$625.50** |

**Nota**: Shield Advanced se distribuye entre múltiples aplicaciones empresariales.

### **5. Storage - Backend Only**

| Servicio                           | Especificación         | Costo Mensual (USD) |
| ---------------------------------- | ----------------------- | ------------------: |
| Amazon S3 Standard                 | 50 GB                   |               $1.15 |
| S3 Requests                        | PUT/GET requests        |               $0.85 |
| **Subtotal Storage Backend** | **Standard Tier** |     **$2.00** |

## AWS DevOps - Backend Only

### **Configuración Optimizada para Backend**

**Justificación de la Optimización:**

- **Proyectos reducidos**: Solo APIs backend (sin frontend React)
- **Pipelines simplificados**: Un pipeline por API
- **Usuarios reducidos**: 3 desarrolladores + 1 DevOps Lead
- **Registry optimizado**: Solo imágenes de contenedores backend

#### **AWS CodeCommit - Backend Only**

| Tipo                          |                 Cantidad | Especificación                    | Costo Mensual (USD) |
| ----------------------------- | -----------------------: | ---------------------------------- | ------------------: |
| Repositorios                  |                  3 repos | APIs .NET Core (sin frontend)      |               $0.00 |
| Storage                       |                     5 GB | Código fuente backend únicamente |               $0.00 |
| **Subtotal CodeCommit** | **3 Repositorios** | **Total**                    |     **$0.00** |

#### **AWS CodeBuild - Backend Only**

| Tipo                         |              Cantidad | Especificación    | Costo Mensual (USD) |
| ---------------------------- | --------------------: | ------------------ | ------------------: |
| Build Minutes (General)      |           400 minutos | .NET Core builds   |              $20.00 |
| Build Minutes (ARM)          |           200 minutos | Builds optimizados |              $16.00 |
| **Subtotal CodeBuild** | **600 minutos** | **Total**    |    **$36.00** |

#### **Amazon ECR - Backend Only**

| Tipo                   |              Cantidad | Especificación                   | Costo Mensual (USD) |
| ---------------------- | --------------------: | --------------------------------- | ------------------: |
| Storage                |                 20 GB | Imágenes de contenedores backend |              $20.00 |
| Data Transfer          |                  5 GB | Push/Pull de imágenes            |               $5.00 |
| **Subtotal ECR** | **25 GB Total** | **Total**                   |    **$25.00** |

#### **AWS CodePipeline - Backend Only**

| Tipo                            |              Cantidad | Especificación           | Costo Mensual (USD) |
| ------------------------------- | --------------------: | ------------------------- | ------------------: |
| Active Pipelines                |           3 pipelines | CI/CD para APIs backend   |              $30.00 |
| Pipeline Executions             |              150 runs | Deployments automatizados |               $0.00 |
| **Subtotal CodePipeline** | **3 Pipelines** | **Total**           |    **$30.00** |

#### **Otros Servicios DevOps - Backend Only**

| Servicio                 | Especificación      | Costo Mensual (USD) |
| ------------------------ | -------------------- | ------------------: |
| CloudWatch Logs          | Logs de aplicaciones |               $8.00 |
| Systems Manager          | Parameter Store      |               $3.00 |
| **Subtotal Otros** | **Monitoreo**  |    **$11.00** |

### **Resumen de Costos AWS DevOps Backend Only**

| Componente                 |                           Costo Mensual (USD) |                            Costo Mensual (MXN) | Costo Anual (USD) | Costo Anual (MXN) |
| -------------------------- | --------------------------------------------: | ---------------------------------------------: | ----------------: | ----------------: |
| CodeCommit                 |                   $0.00 |               $0.00 |                      $0.00 |             $0.00 |                   |                   |
| CodeBuild                  |                  $36.00 |             $648.00 |                    $432.00 |         $7,776.00 |                   |                   |
| ECR                        |                  $25.00 |             $450.00 |                    $300.00 |         $5,400.00 |                   |                   |
| CodePipeline               |                  $30.00 |             $540.00 |                    $360.00 |         $6,480.00 |                   |                   |
| Otros Servicios            |                  $11.00 |             $198.00 |                    $132.00 |         $2,376.00 |                   |                   |
| **Total AWS DevOps** | **$102.00** |       **$1,836.00** | **$1,224.00** |     **$22,032.00** |                   |                   |

### **Comparación DevOps: Original vs Backend Only**

| Componente           |               Original (USD) | Backend Only (USD) | Ahorro (USD) | % Ahorro |
| -------------------- | ---------------------------: | -----------------: | -----------: | -------: |
| **AWS DevOps** | $312.00 |            $102.00 |            $210.00 |        67.3% |          |

**Nota**: Ahorro significativo de $210/mes ($2,520/año) eliminando infraestructura de frontend.

## **Comparación: Propuesta Original vs Backend Only**

| Componente              |                                  Original (USD) |  Backend Only (USD) |    Ahorro (USD) | % Ahorro |
| ----------------------- | ----------------------------------------------: | ------------------: | --------------: | -------: |
| ECS Fargate             |                     $798.50 |           $515.04 |             $283.46 |           35.5% |
| API Gateway             |                     $285.00 |           $285.00 |               $0.00 |              0% |          |
| Networking              |                     $812.00 |           $812.00 |               $0.00 |              0% |          |
| Seguridad               |                     $625.50 |           $625.50 |               $0.00 |              0% |          |
| Storage                 |                       $2.00 |             $2.00 |               $0.00 |              0% |          |
| AWS DevOps              |                     $312.00 |           $102.00 |             $210.00 |           67.3% |
| **TOTAL MENSUAL** |  **$2,835.00** |      **$2,341.54** |   **$493.46** | **17.4%** |
| **TOTAL ANUAL**   | **$34,020.00** |     **$28,098.48** | **$5,921.52** | **17.4%** |

### **Beneficios de la Versión Backend Only:**

1. **Ahorro Significativo**: $493.46 USD/mes ($5,921.52 USD/año)
2. **Menor Complejidad**: Solo gestionar servicios backend
3. **Deployment Simplificado**: Pipelines enfocados en APIs
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
4. **Monitoreo**: Implementar alertas proactivas para APIs con CloudWatch

---

**Documento preparado para:** Bradescard México
**Preparado por:** Equipo de Arquitectura Cloud
**Versión:** Backend Only Optimizada
**Fecha:** 24 de Septiembre, 2025
