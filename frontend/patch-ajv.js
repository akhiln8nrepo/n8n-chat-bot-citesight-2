const fs = require('fs');
const path = require('path');

// The broken nested ajv inside schema-utils
const nestedAjvDir = path.join(
  __dirname,
  'node_modules/schema-utils/node_modules/ajv'
);

// The correct top-level ajv
const topLevelAjvDir = path.join(
  __dirname,
  'node_modules/ajv'
);

if (fs.existsSync(nestedAjvDir)) {
  console.log('🔧 Found nested broken ajv — removing it...');
  fs.rmSync(nestedAjvDir, { recursive: true, force: true });
  console.log('✅ Removed nested ajv — will now use top-level ajv@8');
} else {
  console.log('✅ No nested ajv found — nothing to patch');
}

// Also check ajv-keywords nested copy
const nestedAjvKeywordsDir = path.join(
  __dirname,
  'node_modules/schema-utils/node_modules/ajv-keywords'
);

if (fs.existsSync(nestedAjvKeywordsDir)) {
  console.log('🔧 Found nested broken ajv-keywords — removing it...');
  fs.rmSync(nestedAjvKeywordsDir, { recursive: true, force: true });
  console.log('✅ Removed nested ajv-keywords');
} else {
  console.log('✅ No nested ajv-keywords found — nothing to patch');
}
