const path = require('path');

module.exports = {
  webpack: {
    configure: (webpackConfig) => {

      // Fix the @ alias to point to src folder
      webpackConfig.resolve = webpackConfig.resolve || {};
      webpackConfig.resolve.alias = {
        ...webpackConfig.resolve.alias,
        '@': path.resolve(__dirname, 'src'),
      };

      return webpackConfig;
    },
  },
};
