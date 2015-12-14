module.exports = function(grunt) {

    grunt.initConfig({
        babel: {
            options: {
                sourceMap: true,
                presets: ['es2015', 'react']
            },
            server: {
                files: {
                    'dist/server.js': 'src/server.js',
                    'dist/edit-item-box.js': 'src/edit-item-box.js'
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-babel');

    grunt.registerTask('default', ['babel']);

};
