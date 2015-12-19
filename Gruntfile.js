module.exports = function(grunt) {

    grunt.initConfig({
        babel: {
            options: {
                sourceMap: true,
                presets: ['es2015', 'react']
            },
            server: {
                files: [
                    {
                        expand: true,
                        cwd: 'src/',
                        src: ['*.js'],
                        dest: 'dist/'
                    }
                ]
            }
        },
        browserify: {
            client: {
                files: {
                    'static/client.js': ['dist/client.js']
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-babel');
    grunt.loadNpmTasks('grunt-browserify');

    grunt.registerTask('default', ['babel', 'browserify']);

};
