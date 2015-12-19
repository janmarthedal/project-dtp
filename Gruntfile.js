module.exports = function(grunt) {

    grunt.initConfig({
        babel: {
            options: {
                sourceMap: true,
                presets: ['es2015', 'react'],
                plugins: ['transform-runtime']
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
                    'static/core.js': ['dist/core.js'],
                    'static/create.js': ['dist/create.js'],
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-babel');
    grunt.loadNpmTasks('grunt-browserify');

    grunt.registerTask('default', ['babel', 'browserify']);

};
