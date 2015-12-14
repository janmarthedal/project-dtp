import express from 'express';
import consolidate from 'consolidate';
import handlebars from 'handlebars';

var app = express();

handlebars.registerPartial({
    header: handlebars.compile('<!doctype html>' +
                '<html><head><title>{{title}}</title></head>' +
                '<body><h1>{{title}}</h1>'),
    footer: handlebars.compile('</body></html>')
});

app.engine('html', consolidate.handlebars);
app.set('view engine', 'html');
app.set('views', __dirname + '/../views');

app.get('/', function(req, res){
  res.render('index', {title: 'Test title'});
});

app.listen(3000);
console.log('Express server listening on port 3000');
