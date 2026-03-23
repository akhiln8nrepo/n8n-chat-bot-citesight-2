const fs = require('fs');
const path = require('path');

// List of all known locations with broken nested ajv/ajv-keywords
const pathsToRemove = [
  // schema-utils nested copies
  'node_modules/schema-utils/node_modules/ajv',
  'node_modules/schema-utils/node_modules/ajv-keywords',

  // fork-ts-checker-webpack-plugin nested copies
  'node_modules/fork-ts-checker-webpack-plugin/node_modules/schema-utils',
  'node_modules/fork-ts-checker-webpack-plugin/node_modules/ajv',
  'node_modules/fork-ts-checker-webpack-plugin/node_modules/ajv-keywords',

  // react-dev-utils nested copies
  'node_modules/react-dev-utils/node_modules/schema-utils',
  'node_modules/react-dev-utils/node_modules/ajv',
  'node_modules/react-dev-utils/node_modules/ajv-keywords',

  // terser-webpack-plugin nested copies
  'node_modules/terser-webpack-plugin/node_modules/schema-utils',
  'node_modules/terser-webpack-plugin/node_modules/ajv',
  'node_modules/terser-webpack-plugin/node_modules/ajv-keywords',

  // css-minimizer-webpack-plugin nested copies
  'node_modules/css-minimizer-webpack-plugin/node_modules/schema-utils',
  'node_modules/css-minimizer-webpack-plugin/node_modules/ajv',
  'node_modules/css-minimizer-webpack-plugin/node_modules/ajv-keywords',
];

let patchedCount = 0;

pathsToRemove.forEach((relativePath) => {
  const fullPath = path.join(__dirname, relativePath);
  if (fs.existsSync(fullPath)) {
    console.log(`🔧 Removing: ${relativePath}`);
    fs.rmSync(fullPath, { recursive: true, force: true });
    patchedCount++;
  }
});

if (patchedCount === 0) {
  console.log('✅ No nested broken packages found — nothing to patch');
} else {
  console.log(`✅ Patched ${patchedCount} nested package(s) successfully`);
}
