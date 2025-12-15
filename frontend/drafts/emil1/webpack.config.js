const path = require('path');
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
    entry: './src/main.ts',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'dist'),
        assetModuleFilename: 'resources/[name][ext]', // Don't mangle image filenames to hashes
    },
    experiments: {
        asyncWebAssembly: true
    },
    mode: 'development',
    resolve: {
        extensions: ['.ts', '.js']
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: 'ts-loader',
                exclude: /node_modules/
            },
            {
                // TODO: Optimize css by minimizing for production
                test: /\.css$/,
                use: ["style-loader", "css-loader"],
            },
            {
                test: /\.(png|svg|jpg|jpeg|gif)$/i,
                type: "asset/resource"
            },
        ]
    },

    plugins: [
        new HtmlWebpackPlugin({
            template: "./assets/index.html",
            filename: "index.html",
            minify: 'auto',
            inject: true
        }),
    ],
};