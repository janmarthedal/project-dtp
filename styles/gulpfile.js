const gulp = require('gulp');
const watch = require('gulp-watch');
const less = require('gulp-less');

gulp.task('default', function() {
    return gulp.src('./less/main.less')
        .pipe(less())
        .pipe(gulp.dest('../main/static/main/'));
});

gulp.task('watch', ['default'], function() {
    return watch('./less/**/*', function() {
        gulp.start('default');
    });
});
