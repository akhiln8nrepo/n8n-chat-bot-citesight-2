const fs = require('fs');
const path = require('path');

// Remove ALL nested node_modules that could have conflicting versions
const pathsToRemove = [
  'node_modules/schema-utils/node_modules',
  'node_modules/fork-ts-checker-webpack-plugin/node_modules',
  'node_modules/terser-webpack-plugin/node_modules',
  'node_modules/css-minimizer-webpack-plugin/node_modules',
  'node_modules/webpack/node_modules',
  'node_modules/webpack-dev-server/node_modules',
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
  console.log('✅ No nested packages found — nothing to patch');
} else {
  console.log(`✅ Cleared ${patchedCount} nested node_modules folder(s)`);
}
