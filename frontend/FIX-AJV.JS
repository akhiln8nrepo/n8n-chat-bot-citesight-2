const fs = require('fs');
const path = require('path');

// Path to the broken nested ajv-keywords
const brokenPath = path.join(
  __dirname,
  'node_modules/schema-utils/node_modules/ajv-keywords/dist/definitions/typeof.js'
);

// Check if the broken file exists
if (fs.existsSync(brokenPath)) {
  console.log('Found broken ajv-keywords — patching...');

  // Replace the broken require with a safe stub
  const fixedContent = `
"use strict";
// Patched by fix-ajv.js to resolve MODULE_NOT_FOUND error
const defined = (v) => v !== undefined;
module.exports = defined;
`;

  fs.writeFileSync(brokenPath, fixedContent);
  console.log('Patch applied successfully!');
} else {
  console.log('No patch needed — file not found at expected path.');
}
