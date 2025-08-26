const path = require('path');

module.exports = {
    entry: path.resolve(__dirname, 'static/js/react/index.js'),
output: {
    path: path.resolve(__dirname, 'static/js/dist'),
    filename: 'bundle.js',
},
    module: {
        rules: [
            {
                test: /\.jsx?$/, // Пошук JSX або JS файлів
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env', '@babel/preset-react'], // Пресети Babel
                    },
                },
            },
        ],
    },
    resolve: {
        extensions: ['.js', '.jsx'], // Підтримувані розширення файлів
    },
};