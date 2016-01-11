var webpack = require('webpack');
var path = require('path');

module.exports = {
    entry: {
        core: ['./src/core', './src/edit-item-form', 'react', 'react-dom'],
        create: './src/create'
    },
    output: {
        path: path.join(__dirname, 'static'),
        filename: '[name].js'
    },
    externals: {
        // require("mathjax") is external and available
        //  on the global var MathJax
        "mathjax": "MathJax"
    },
    plugins: [
        new webpack.optimize.CommonsChunkPlugin('core', 'core.js')
    ],
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                exclude: /(node_modules|bower_components)/,
                loader: 'babel',
                query: {
                    presets: ['react', 'es2015'],
                    plugins: ['transform-runtime']
                }
            }
        ]
    }
};
