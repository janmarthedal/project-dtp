var webpack = require('webpack');
var path = require('path');

module.exports = {
    entry: {
        core: ['./src/core', './src/rx', 'react', 'react-dom'],
        edit: './src/edit',
    },
    output: {
        path: path.join(__dirname, 'static'),
        filename: '[name].js'
    },
    plugins: [
        new webpack.optimize.CommonsChunkPlugin('core', 'core.js')
    ],
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel',
                query: {
                    presets: ['react', 'es2015'],
                    plugins: ['transform-runtime']
                }
            }
        ]
    }
};
