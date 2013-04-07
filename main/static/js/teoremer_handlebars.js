(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['search_list_container'] = template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  var buffer = "";


  buffer += "\n<table class=\"table\">\n<tbody>\n</tbody>\n</table>\n";
  return buffer;
  });
templates['search_list_item'] = template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  var buffer = "", stack1, stack2, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = "", stack1;
  buffer += " (";
  if (stack1 = helpers.pritags) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.pritags; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + ")";
  return buffer;
  }

function program3(depth0,data) {
  
  var buffer = "";
  buffer += "<span class=\"tag\">"
    + escapeExpression((typeof depth0 === functionType ? depth0.apply(depth0) : depth0))
    + "</span>";
  return buffer;
  }

  buffer += "<td>\n<div><a href=\"/";
  if (stack1 = helpers.id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">";
  if (stack1 = helpers.itemname) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.itemname; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1);
  stack1 = helpers['if'].call(depth0, depth0.pritags, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "</a></div>\n<div><small class=\"pull-right\">by "
    + escapeExpression(((stack1 = ((stack1 = depth0.author),stack1 == null || stack1 === false ? stack1 : stack1.name)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + " at ";
  if (stack2 = helpers.published_at) { stack2 = stack2.call(depth0, {hash:{},data:data}); }
  else { stack2 = depth0.published_at; stack2 = typeof stack2 === functionType ? stack2.apply(depth0) : stack2; }
  buffer += escapeExpression(stack2)
    + "</small>\n";
  stack2 = helpers.each.call(depth0, depth0.sectags, {hash:{},inverse:self.noop,fn:self.program(3, program3, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "</div>\n</td>";
  return buffer;
  });
templates['tag_list_input'] = template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression;


  buffer += "<p id=\"";
  if (stack1 = helpers.prefix) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.prefix; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "-tag-list\"></p>\n<div class=\"input-append\">\n  <input id=\"";
  if (stack1 = helpers.prefix) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.prefix; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "-tag-name\" class=\"span8\" type=\"text\">\n  <button id=\"";
  if (stack1 = helpers.prefix) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.prefix; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "-tag-add\" class=\"btn\" type=\"button\">Add</button>\n</div>\n";
  return buffer;
  });
})();