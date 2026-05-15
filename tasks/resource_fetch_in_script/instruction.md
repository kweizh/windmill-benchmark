# Windmill Script with Typed Resource Parameter

## Background

Windmill allows scripts to receive pre-configured **resources** as typed parameters. A resource is a JSON object stored in Windmill at a path such as `u/user/my_db`. The script declares a matching TypeScript type and Windmill injects the resource at runtime.

You must write a TypeScript Windmill script that accepts a PostgreSQL resource parameter and a table name, then returns a mock result object demonstrating the resource was received correctly.

## Requirements

- Create a TypeScript Windmill script at `/home/user/windmill-project/f/scripts/db_row_count.ts`.
- Create its companion YAML metadata file at `/home/user/windmill-project/f/scripts/db_row_count.script.yaml`.

## Implementation Guide

1. Create the project directory structure:
   ```
   mkdir -p /home/user/windmill-project/f/scripts
   ```

2. Create `/home/user/windmill-project/f/scripts/db_row_count.ts` with the following structure:
   - Define a `Postgresql` type inline:
     ```typescript
     type Postgresql = {
       host: string;
       port: number;
       user: string;
       dbname: string;
       sslmode: string;
       password: string;
     };
     ```
   - Export a `main` function with signature:
     ```typescript
     export async function main(db: Postgresql, table_name: string)
     ```
   - The function must return:
     ```typescript
     {
       host: db.host,
       dbname: db.dbname,
       table: table_name,
       query: `SELECT COUNT(*) FROM ${table_name}`,
       note: "Resource received successfully"
     }
     ```

3. Create `/home/user/windmill-project/f/scripts/db_row_count.script.yaml` with the following content:
   ```yaml
   summary: Count rows in a database table using a PostgreSQL resource
   description: Accepts a Postgresql resource and table name, returns a mock query result object
   schema:
     $schema: 'https://json-schema.org/draft/2020-12/schema'
     type: object
     order:
       - db
       - table_name
     properties:
       db:
         description: PostgreSQL database resource
         type: object
         format: resource-postgresql
       table_name:
         description: Name of the table to count rows in
         type: string
         default: ''
     required:
       - db
       - table_name
   language: ts
   kind: script
   tag: ''
   ```

## Constraints

- Project path: `/home/user/windmill-project`
- Do not connect to any live database — this is a mock script.
- Use TypeScript (`.ts` extension) as the script language.
- Do not use `import * as wmill from 'windmill-client'` — the resource is passed directly as a typed parameter.
- The `Postgresql` type must be defined in the script file itself.
