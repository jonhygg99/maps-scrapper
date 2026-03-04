# Export Module

A modular, extensible data export system supporting CSV, Excel, and JSON formats with proper error handling, configuration management, and backward compatibility.

## 📁 Structure

```
export/
├── __init__.py          # Main entry point and public API
├── base.py             # Abstract base classes and result containers
├── config.py           # Export configuration and constants
├── file_manager.py     # File operations and directory management
├── csv_exporter.py     # CSV-specific export logic
├── excel_exporter.py    # Excel-specific export with formatting
├── json_exporter.py     # JSON export with metadata support
├── exporter_factory.py  # Factory pattern for exporter creation
└── README.md           # This documentation
```

## 🚀 Quick Start

### Modern API (Recommended)

```python
from src.utils.export import ExporterFactory, export_data

# Using factory
factory = ExporterFactory()
result = factory.export_data(data, 'csv', 'output.csv')

if result.success:
    print(f"Exported to: {result.file_path}")
    print(f"Records: {result.records_exported}")
else:
    print(f"Errors: {result.errors}")
```

### Legacy API (Backward Compatible)

```python
from src.utils.export import DataExporter

# Traditional usage
exporter = DataExporter()
file_path = exporter.to_csv(data, 'output.csv')
```

## 📋 Supported Formats

| Format | Extension | Features |
|---------|------------|----------|
| CSV | `.csv` | Configurable columns, UTF-8-BOM encoding |
| Excel | `.xlsx` | Auto column width adjustment, formatting |
| JSON | `.json` | Optional metadata, pretty printing |

## 🔧 Advanced Usage

### Custom Exporters

```python
from src.utils.export import ExporterFactory, CSVExporter

# Create custom CSV exporter with specific columns
csv_exporter = CSVExporter(columns=['name', 'email', 'phone'])
result = csv_exporter.export(data, 'custom.csv')
```

### Multiple Formats

```python
factory = ExporterFactory()
results = factory.export_to_multiple_formats(
    data, 
    ['csv', 'excel', 'json'],
    base_filename='report'
)

for format_type, result in results.items():
    if result.success:
        print(f"{format_type}: {result.file_path}")
```

### Configuration

```python
from src.utils.export import ExportConfig

# Get format-specific configuration
csv_config = ExportConfig.get_config_for_format('csv')
excel_config = ExportConfig.get_config_for_format('excel')

# Get default columns
columns = ExportConfig.DEFAULT_CSV_COLUMNS
```

## 🏗️ Architecture

### Core Components

- **BaseExporter**: Abstract base class for all exporters
- **ExportResult**: Standardized result container with metadata
- **FileManager**: File path operations and directory management
- **ExportConfig**: Centralized configuration management

### Exporters

- **CSVExporter**: Handles CSV format with configurable columns
- **ExcelExporter**: Excel export with auto-formatting
- **JSONExporter**: JSON export with optional metadata

### Factory Pattern

- **ExporterFactory**: Creates exporters and manages operations
- **Registry System**: Easy addition of new export formats

## 📝 Error Handling

All export operations return `ExportResult` objects:

```python
@dataclass
class ExportResult:
    success: bool              # Operation success status
    file_path: Optional[str]    # Output file path
    records_exported: int      # Number of records processed
    errors: List[str]          # Error messages
    metadata: Dict[str, Any]    # Additional metadata
```

## 🔌 Extending the System

### Adding New Export Format

1. Create new exporter class:

```python
from .base import BaseExporter, ExportResult

class MyExporter(BaseExporter):
    def __init__(self):
        super().__init__("MyExporter")
    
    def export(self, data, filename=None, output_dir=None) -> ExportResult:
        # Implementation here
        pass
```

2. Register with factory:

```python
from .exporter_factory import ExporterFactory

ExporterFactory.register_exporter('myformat', MyExporter)
```

## 📊 Performance

- **Memory Efficient**: Streaming writes for large datasets
- **Type Safe**: Full type hints throughout
- **Error Resilient**: Comprehensive error handling
- **Configurable**: Flexible behavior through configuration

## 🔄 Migration from Legacy

The module maintains full backward compatibility. Existing code using:

```python
from src.utils.exporter import DataExporter
```

Will continue to work without changes, but new code should use:

```python
from src.utils.export import DataExporter
```

## 🐛 Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure output directory is writable
2. **Import Errors**: Check file paths and dependencies
3. **Format Support**: Use `get_available_formats()` to check support

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Version History

- **v2.0.0**: Modular refactor with factory pattern
- **v1.x**: Legacy monolithic exporter

## 🤝 Contributing

When adding new export formats:

1. Follow the `BaseExporter` interface
2. Include comprehensive error handling
3. Add format-specific configuration
4. Update this documentation
5. Add tests for new functionality

## 📄 License

This module is part of the Google Maps Scraper project.
