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
        },
        browserify: {
            options: {
                ignore: 'react'
            },
            client: {
                files: {
                    'dist/client.js': ['dist/edit-item-box.js']
                },
                exclude: 'react'
            }
        }
    });

    grunt.loadNpmTasks('grunt-babel');
    grunt.loadNpmTasks('grunt-browserify');

    grunt.registerTask('default', ['babel', 'browserify']);

};
