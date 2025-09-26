# Diagramas PNG - API Auditoría Bradescard México

Este directorio contiene las imágenes PNG de los diagramas Mermaid generados para el documento Word de la propuesta.

## Imágenes Generadas

### 1. **flujo-proceso-originacion.png** (233 KB)
- **Dimensiones**: 1094 x 3772 px
- **Descripción**: Flujo completo del proceso de originación de tarjetas de crédito
- **Contenido**: 51 eventos desde inicio hasta activación de tarjeta
- **Ubicación en documento**: Sección "1. Contexto del Negocio y Taxonomía de Eventos"

### 2. **arquitectura-azure.png** (159 KB)  
- **Dimensiones**: 1778 x 1520 px
- **Descripción**: Arquitectura completa de la solución Azure
- **Contenido**: 6 capas (Ingreso, API, Procesamiento, Persistencia, Compliance, Analytics)
- **Ubicación en documento**: Sección "2. Arquitectura de Solución Azure"

### 3. **modelo-base-datos.png** (369 KB)
- **Dimensiones**: 1904 x 1631 px
- **Descripción**: Modelo entidad-relación de la base de datos
- **Contenido**: 6 tablas principales con relaciones y campos clave
- **Ubicación en documento**: Sección "3. Modelo de Datos y Compliance"

## Cómo usar en Microsoft Word

### Paso 1: Insertar Imágenes
1. Abrir el documento `API_Auditoria_Originacion_Bradescard_Mexico.docx`
2. Navegar a la sección correspondiente de cada diagrama
3. Eliminar el texto del diagrama Mermaid (que no se renderiza correctamente)
4. Insertar → Imágenes → Este dispositivo
5. Seleccionar la imagen PNG correspondiente

### Paso 2: Formato Recomendado
- **Diseño**: "En línea con el texto" o "Cuadrado"
- **Ancho**: 100% del ancho de página (ajustar automáticamente)
- **Calidad**: Mantener calidad original
- **Título**: Agregar pie de imagen descriptivo

### Paso 3: Pies de Imagen Sugeridos

#### Para flujo-proceso-originacion.png:
```
Figura 1: Flujo Completo del Proceso de Originación de Tarjetas de Crédito
Muestra los 51 eventos estandarizados desde la solicitud inicial hasta la activación 
de la tarjeta, incluyendo integración con Buró Identidad, Business Rules Engine y Core Bancario.
```

#### Para arquitectura-azure.png:
```
Figura 2: Arquitectura de Solución Azure para Auditoría de Originación
Arquitectura de 6 capas diseñada para compliance CNBV, alta disponibilidad 
y procesamiento de 10,000+ aplicaciones mensuales.
```

#### Para modelo-base-datos.png:
```
Figura 3: Modelo de Datos con Always Encrypted y Particionamiento
Esquema de base de datos optimizado para auditoría financiera con encriptación 
de datos PII y cumplimiento de regulaciones mexicanas.
```

## Ubicaciones Exactas en el Documento

### Sección 1 - Después del texto:
```
"### Proceso Estándar de Originación de Tarjetas de Crédito"
```
→ **Insertar**: flujo-proceso-originacion.png

### Sección 2 - Después del texto:
```
"## Arquitectura Rediseñada para Auditoría Financiera"
```
→ **Insertar**: arquitectura-azure.png  

### Sección 3 - Después del texto:
```
"### Esquema de Base de Datos Especializado"
```
→ **Insertar**: modelo-base-datos.png

## Notas Técnicas

- **Resolución**: Todas las imágenes están en alta resolución (1920x1080 base)
- **Formato**: PNG con fondo blanco para mejor integración en documentos
- **Tamaño**: Optimizadas para impresión y visualización digital
- **Compatibilidad**: Compatible con todas las versiones de Microsoft Word

## Archivos Fuente

Los archivos `.mmd` contienen el código fuente Mermaid original para futuras modificaciones:
- `flujo-proceso-originacion.mmd`
- `arquitectura-azure.mmd`  
- `modelo-base-datos.mmd`

Para regenerar las imágenes después de modificaciones:
```bash
mmdc -i [archivo].mmd -o [archivo].png -w 1920 -H 1080 --backgroundColor white
```