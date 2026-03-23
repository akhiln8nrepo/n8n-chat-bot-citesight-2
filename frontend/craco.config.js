const path = require('path');

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Force webpack to resolve ajv from the correct location
      webpackConfig.resolve = webpackConfig.resolve || {};
      webpackConfig.resolve.alias = webpackConfig.resolve.alias || {};
      
      // Point all ajv imports to the single correct version
      webpackConfig.resolve.alias['ajv'] = path.resolve(
        __dirname,
        'node_modules/ajv'
      );
      webpackConfig.resolve.alias['ajv-keywords'] = path.resolve(
        __dirname,
        'node_modules/ajv-keywords'
      );
      webpackConfig.resolve.alias['schema-utils'] = path.resolve(
        __dirname,
        'node_modules/schema-utils'
      );

      return webpackConfig;
    },
  },
};
