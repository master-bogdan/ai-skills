# Node.js — Swagger Setup

## Packages

```sh
npm install swagger-ui-express swagger-jsdoc
npm install -D @types/swagger-ui-express @types/swagger-jsdoc
# If project uses Zod, also install:
npm install zod-to-json-schema
```

## Middleware registration

Add to server entrypoint after other middleware, before catch-all error handler:

```ts
import swaggerUi from 'swagger-ui-express';
import swaggerJsdoc from 'swagger-jsdoc';

const swaggerSpec = swaggerJsdoc({
  definition: {
    openapi: '3.0.0',
    info: {
      title: process.env.npm_package_name ?? 'API',
      version: process.env.npm_package_version ?? '1.0.0',
    },
  },
  apis: ['./src/routes/**/*.ts', './src/controllers/**/*.ts'],
});

app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
```

## Route annotation format

Add JSDoc annotations directly above route handlers or controller functions:

```ts
/**
 * @openapi
 * /orders:
 *   get:
 *     summary: List orders for the authenticated user
 *     tags: [Orders]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: List of orders
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Order'
 *       401:
 *         description: Unauthorized
 */
router.get('/orders', requireAuth, listOrdersController);

/**
 * @openapi
 * /orders:
 *   post:
 *     summary: Create a new order
 *     tags: [Orders]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/CreateOrderInput'
 *     responses:
 *       201:
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Order'
 */
router.post('/orders', requireAuth, createOrderController);
```

## Model schema annotation

Define schemas in a dedicated types or dto file:

```ts
/**
 * @openapi
 * components:
 *   schemas:
 *     Order:
 *       type: object
 *       required: [id, status, total]
 *       properties:
 *         id:
 *           type: string
 *         status:
 *           type: string
 *           enum: [pending, processing, shipped, cancelled]
 *         total:
 *           type: number
 *         createdAt:
 *           type: string
 *           format: date-time
 */
```

## Static spec generation script

Create `scripts/generate-swagger.ts`:

```ts
import fs from 'fs';
import path from 'path';
import swaggerJsdoc from 'swagger-jsdoc';

const spec = swaggerJsdoc({
  definition: {
    openapi: '3.0.0',
    info: { title: 'API', version: '1.0.0' },
  },
  apis: ['./src/routes/**/*.ts', './src/controllers/**/*.ts'],
});

// Write full spec
fs.mkdirSync('docs/schemas', { recursive: true });
fs.writeFileSync('docs/swagger.json', JSON.stringify(spec, null, 2));

// Write individual schema files
const schemas = (spec as any).components?.schemas ?? {};
for (const [name, schema] of Object.entries(schemas)) {
  fs.writeFileSync(
    path.join('docs/schemas', `${name}.json`),
    JSON.stringify(schema, null, 2),
  );
}

console.log(`Generated docs/swagger.json with ${Object.keys(schemas).length} schemas`);
```

Add to `package.json`:
```json
{
  "scripts": {
    "swagger": "ts-node scripts/generate-swagger.ts"
  }
}
```

## Zod schema → JSON Schema (if project uses Zod)

```ts
import { zodToJsonSchema } from 'zod-to-json-schema';
import { createOrderSchema } from '../dto/create-order.dto';

const jsonSchema = zodToJsonSchema(createOrderSchema, 'CreateOrderInput');
fs.writeFileSync('docs/schemas/CreateOrderInput.json', JSON.stringify(jsonSchema, null, 2));
```
