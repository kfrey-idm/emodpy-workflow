# Ingest form age bin format

The ingest form uses a particular format for age bins. These age bins are used on multiple sheets: **Site**, 
**Analyzers**, and **observational data** sheets.

The format is left-inclusive and right-exclusive, and specified exactly as follows with no whitespace:

```bash
[MIN:MAX)
```

Age bins are interpreted as: MIN <= age < MAX

!!! Important
    MIN and MAX ages in an age bin must be integers.

For example, the following specifies: 15 <= age <50 (e.g., 15, 20.5, 49.999 are included, but not 14.9, 50, or 75.5)

```bash
[15:50)
```