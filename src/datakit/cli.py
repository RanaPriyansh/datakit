#!/usr/bin/env python3
"""
CLI for datakit – Data format converter toolkit.
"""

import argparse
import sys
import json
import textwrap
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog="datakit",
        description="📊 datakit – Data format converter toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              datakit convert data.csv data.json
              datakit validate data.json --schema schema.json
              datakit filter data.json --condition '{"age": {"gt": 18}}'
              datakit merge a.json b.json --on id --how left
              datakit summary data.csv
            """)
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # ---- Convert command ----
    convert_parser = subparsers.add_parser("convert", help="Convert between data formats")
    convert_parser.add_argument("input", help="Input data file")
    convert_parser.add_argument("output", help="Output data file")
    convert_parser.add_argument("--from-format", help="Input format (auto-detect if omitted)")
    convert_parser.add_argument("--to-format", help="Output format (auto-detect if omitted)")
    
    # ---- Validate command ----
    validate_parser = subparsers.add_parser("validate", help="Validate data against schema")
    validate_parser.add_argument("input", help="Input data file")
    validate_parser.add_argument("--schema", help="Schema file (JSON or YAML)")
    validate_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # ---- Filter command ----
    filter_parser = subparsers.add_parser("filter", help="Filter data by conditions")
    filter_parser.add_argument("input", help="Input data file")
    filter_parser.add_argument("--condition", required=True, help="Filter conditions (JSON)")
    filter_parser.add_argument("-o", "--output", help="Output file")
    filter_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # ---- Select command ----
    select_parser = subparsers.add_parser("select", help="Select specific fields")
    select_parser.add_argument("input", help="Input data file")
    select_parser.add_argument("--fields", required=True, help="Comma-separated list of fields")
    select_parser.add_argument("-o", "--output", help="Output file")
    select_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # ---- Merge command ----
    merge_parser = subparsers.add_parser("merge", help="Merge datasets")
    merge_parser.add_argument("input1", help="First data file")
    merge_parser.add_argument("input2", help="Second data file")
    merge_parser.add_argument("--on", help="Field to merge on")
    merge_parser.add_argument("--how", choices=["inner", "left", "right", "outer"], 
                             default="outer", help="Join type")
    merge_parser.add_argument("-o", "--output", help="Output file")
    merge_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # ---- Summary command ----
    summary_parser = subparsers.add_parser("summary", help="Generate data summary")
    summary_parser.add_argument("input", help="Input data file")
    summary_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # ---- Sample command ----
    sample_parser = subparsers.add_parser("sample", help="Sample data")
    sample_parser.add_argument("input", help="Input data file")
    sample_parser.add_argument("-n", type=int, default=10, help="Number of samples")
    sample_parser.add_argument("--method", choices=["random", "first", "last"], 
                              default="random", help="Sampling method")
    sample_parser.add_argument("-o", "--output", help="Output file")
    sample_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # ---- Infer schema command ----
    schema_parser = subparsers.add_parser("infer-schema", help="Infer schema from data")
    schema_parser.add_argument("input", help="Input data file")
    schema_parser.add_argument("-o", "--output", help="Output schema file")
    schema_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Version
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "convert":
            cmd_convert(args)
        elif args.command == "validate":
            cmd_validate(args)
        elif args.command == "filter":
            cmd_filter(args)
        elif args.command == "select":
            cmd_select(args)
        elif args.command == "merge":
            cmd_merge(args)
        elif args.command == "summary":
            cmd_summary(args)
        elif args.command == "sample":
            cmd_sample(args)
        elif args.command == "infer-schema":
            cmd_infer_schema(args)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_convert(args):
    from .core import DataConverter
    
    output = DataConverter.convert(
        args.input, args.output,
        input_format=args.from_format,
        output_format=args.to_format
    )
    print(f"Converted {args.input} to {output}", file=sys.stderr)


def cmd_validate(args):
    from .core import DataConverter, DataValidator
    
    dataset = DataConverter.load(args.input)
    
    if args.schema:
        # Load schema from file
        schema_path = Path(args.schema)
        if schema_path.suffix == '.json':
            with open(schema_path, 'r') as f:
                schema = json.load(f)
        elif schema_path.suffix in ['.yaml', '.yml']:
            import yaml
            with open(schema_path, 'r') as f:
                schema = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported schema format: {schema_path.suffix}")
    else:
        # Infer schema
        schema = DataValidator.infer_schema(dataset.as_dicts)
    
    result = DataValidator.validate_schema(dataset.as_dicts, schema)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result['valid']:
            print(f"✓ Valid data ({result['records_checked']} records)")
        else:
            print(f"✗ Invalid data ({len(result['errors'])} errors)")
            for error in result['errors'][:10]:  # Show first 10 errors
                print(f"  {error}")
            if len(result['errors']) > 10:
                print(f"  ... and {len(result['errors']) - 10} more errors")
        
        if result['warnings']:
            print(f"⚠ {len(result['warnings'])} warnings")


def cmd_filter(args):
    from .core import DataConverter, DataFilter
    
    # Parse conditions
    conditions = json.loads(args.condition)
    
    dataset = DataConverter.load(args.input)
    filtered = DataFilter.filter(dataset.as_dicts, conditions)
    
    if args.output:
        # Save to file
        dataset.data = filtered
        DataConverter.save(dataset, args.output)
        print(f"Filtered {len(filtered)} records to {args.output}", file=sys.stderr)
    elif args.json:
        print(json.dumps(filtered, indent=2))
    else:
        for record in filtered[:10]:  # Show first 10 records
            print(json.dumps(record))
        if len(filtered) > 10:
            print(f"... and {len(filtered) - 10} more records")


def cmd_select(args):
    from .core import DataConverter, DataFilter
    
    fields = [f.strip() for f in args.fields.split(',')]
    
    dataset = DataConverter.load(args.input)
    selected = DataFilter.select(dataset.as_dicts, fields)
    
    if args.output:
        dataset.data = selected
        DataConverter.save(dataset, args.output)
        print(f"Selected {len(fields)} fields, saved to {args.output}", file=sys.stderr)
    elif args.json:
        print(json.dumps(selected, indent=2))
    else:
        for record in selected[:10]:
            print(json.dumps(record))
        if len(selected) > 10:
            print(f"... and {len(selected) - 10} more records")


def cmd_merge(args):
    from .core import DataConverter, DataMerger
    
    dataset1 = DataConverter.load(args.input1)
    dataset2 = DataConverter.load(args.input2)
    
    merged = DataMerger.merge(
        dataset1.as_dicts,
        dataset2.as_dicts,
        on=args.on,
        how=args.how
    )
    
    if args.output:
        dataset1.data = merged
        DataConverter.save(dataset1, args.output)
        print(f"Merged datasets ({len(merged)} records) to {args.output}", file=sys.stderr)
    elif args.json:
        print(json.dumps(merged, indent=2))
    else:
        for record in merged[:10]:
            print(json.dumps(record))
        if len(merged) > 10:
            print(f"... and {len(merged) - 10} more records")


def cmd_summary(args):
    from .core import DataConverter, DataSampler
    
    dataset = DataConverter.load(args.input)
    summary = DataSampler.summary(dataset.as_dicts)
    
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Dataset Summary: {args.input}")
        print(f"Records: {summary['records']}")
        print(f"Fields: {', '.join(summary['fields'])}")
        
        if 'missing_values' in summary:
            missing = summary['missing_values']
            if any(v > 0 for v in missing.values()):
                print("\nMissing values:")
                for field, count in missing.items():
                    if count > 0:
                        print(f"  {field}: {count}")
        
        if 'numeric_summary' in summary:
            print("\nNumeric summary:")
            for field, stats in summary['numeric_summary'].items():
                if 'mean' in stats:
                    print(f"  {field}: mean={stats['mean']:.2f}, min={stats['min']}, max={stats['max']}")


def cmd_sample(args):
    from .core import DataConverter, DataSampler
    
    dataset = DataConverter.load(args.input)
    sampled = DataSampler.sample(dataset.as_dicts, n=args.n, method=args.method)
    
    if args.output:
        dataset.data = sampled
        DataConverter.save(dataset, args.output)
        print(f"Sampled {len(sampled)} records to {args.output}", file=sys.stderr)
    elif args.json:
        print(json.dumps(sampled, indent=2))
    else:
        for record in sampled:
            print(json.dumps(record))


def cmd_infer_schema(args):
    from .core import DataConverter, DataValidator
    
    dataset = DataConverter.load(args.input)
    schema = DataValidator.infer_schema(dataset.as_dicts)
    
    if args.output:
        # Save schema to file
        schema_path = Path(args.output)
        if schema_path.suffix == '.json':
            with open(schema_path, 'w') as f:
                json.dump(schema, f, indent=2)
        elif schema_path.suffix in ['.yaml', '.yml']:
            import yaml
            with open(schema_path, 'w') as f:
                yaml.dump(schema, f, default_flow_style=False)
        print(f"Schema saved to {args.output}", file=sys.stderr)
    elif args.json:
        print(json.dumps(schema, indent=2))
    else:
        print("Inferred schema:")
        for field, dtype in schema.items():
            print(f"  {field}: {dtype}")


if __name__ == "__main__":
    main()
