const path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { version } = require('./package.json');

module.exports = (env, argv) => {
  const isProductionBuild = argv.mode === 'production';
  const productionPlugins = [
    new CleanWebpackPlugin(),
  ];

  return {
    entry: {
      yoastworker: path.resolve(__dirname, 'wagtailyoast/static/wagtailyoast/src/js/yoastworker.js'),
      yoastanalysis: path.resolve(__dirname, 'wagtailyoast/static/wagtailyoast/src/js/yoastanalysis.js'),
      styles: path.resolve(__dirname, 'wagtailyoast/static/wagtailyoast/src/scss/styles.scss'),
    },
    output: {
      filename: `static/wagtailyoast/dist/js/[name]${version}.js`,
      chunkFilename: `static/wagtailyoast/dist/js/[name]${version}.js`,
      path: path.resolve(__dirname, 'wagtailyoast/static/wagtailyoast/dist'),
      publicPath: '/',
    },
    module: {
      rules: [
        {
          test: /\.s[ac]ss$/i,
          use: [
            MiniCssExtractPlugin.loader,
            { loader: 'css-loader', options: { url: false } },
            'postcss-loader',
            'sass-loader',
          ],
        },
      ],
    },
    resolve: {
      fallback: {
        buffer: require.resolve('buffer/'),
        url: require.resolve("url/"),
      }
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: `static/wagtailyoast/dist/css/[name]${version}.css`,
      }),
      ...isProductionBuild ? productionPlugins : [],
    ],
    devtool: isProductionBuild ? 'source-map' : false,
    devServer: {
      open: true,
      allowedHosts: 'all',
      proxy: [
        {
          context: ['/'],
          target: 'http://127.0.0.1:4243',
        },
      ],
    },
  };
};
