const gulp = require('gulp');
const babel = require('gulp-babel');

gulp.task('default', () => {
	return gulp.src('src/**/*.js')
		.pipe(babel({
			presets: ['es2015']
		}))
		.pipe(gulp.dest('dst'));
});

gulp.task('test', ['default'], () => {
	return gulp.src('test/**/*.js')
		.pipe(babel({
			presets: ['es2015']
		}))
		.pipe(gulp.dest('dst/test'));
});
