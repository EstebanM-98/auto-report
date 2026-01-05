# Auto Report Generator

Sistema automatizado para la generación de reportes de actividades mensuales en Excel, basado en el historial de commits de repositorios Git. Utiliza DeepSeek (LLM) para procesar los mensajes técnicos y convertirlos en descripciones de tareas profesionales, distribuyéndolas inteligentemente para cumplir con los requerimientos de horas diarias.

## Características

- **Análisis de Commits**: Extrae historial de múltiples repositorios locales.
- **Procesamiento con IA**: Usa DeepSeek para convertir commits en items de timesheet profesionales.
- **Distribución Inteligente**: 
  - Asegura el llenado de todos los días hábiles del mes.
  - Normaliza estrictamente a 8 horas diarias.
  - Maneja días festivos de Colombia.
- **Generación de Excel**: Escribe en una plantilla predefinida (`Seguimiento de actividades 2026.xlsx`) marcando los días trabajados.

## Requisitos

- Python 3.10+
- Acceso a Internet (para la API de DeepSeek).
- Una API Key de DeepSeek.

## Instalación

1. **Clonar el repositorio** (o descargar los archivos).
2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   ```
3. **Activar entorno**:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Configuración**:
   - Crear un archivo `.env` en la raíz (ver `.env.example` o guías) con su `DEEPSEEK_API_KEY`.
   - Editar `src/config/settings.py` para configurar:
     - `REPO_LIST`: Lista de rutas absolutas a sus repositorios locales.
     - `DEFAULT_CLIENT_PROJECT`: Nombre del proyecto/cliente para el reporte.
     - `COUNTRY_CODE`: Código de país para festivos (Default: 'CO').

## Uso

Ejecutar el script principal indicando el mes y año deseado:

```bash
# Ejemplo: Generar reporte para Enero 2026
python src/main.py --month 1 --year 2026
```

### Opciones

- `--dry-run`: Simula la generación imprimiendo las tareas en consola sin modificar el Excel.
- `--repo "PATH"`: Agrega un repositorio adicional para esta ejecución específica.

## Estructura del Proyecto

- `src/core/`: Lógica principal (Cliente Git, Procesador LLM, Distribuidor, Manager Excel).
- `src/config/`: Configuraciones globales.
- `src/utils/`: Utilidades de fechas y festivos.
- `src/static/`: Archivos estáticos (Plantilla Excel).

## Autor
Desarrollado para automatizar reportes de consultoría.
