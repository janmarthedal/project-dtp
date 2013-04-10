(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['search_list_container'] = template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  


  return "<p class=\"pull-right\"><span class=\"label label-info\">date</span> <a href=\"#\">points</a> | \n<span class=\"label label-info\">final</span> <a href=\"#\">review</a></p>\n\n<table class=\"table\">\n<tbody>\n</tbody>\n</table>\n\n<button class=\"btn btn-link pull-right search-list-more\" type=\"button\">Show more</button>\n";
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
(function(window) {

    var $ = window.jQuery;

    var api_prefix = '/api/';

    var teoremer = {}

    function typeset_tag(st) {
        var elems = st.split('$');
        for (var n = 0; n < elems.length; n++) {
            if (n % 2 != 0) {
                elems[n] = '\\(' + elems[n] + '\\)';
            }
        }
        return elems.join('');
    }

    function type_short_to_long(st) {
        switch (st.toUpperCase()) {
            case 'D': return 'definition';
            case 'T': return 'theorem';
            case 'P': return 'proof';
        }
    }

    function capitalize(st) {
        return st.charAt(0).toUpperCase() + st.slice(1);
    }

    teoremer.TagItem = Backbone.Model.extend({
    });

    teoremer.TagList = Backbone.Collection.extend({
        model : teoremer.TagItem
    });

    teoremer.TagItemView = Backbone.View.extend({
        tagName : 'span',
        className : 'tag',
        events : {
            'click .delete-tag' : 'remove'
        },
        initialize : function() {
            _.bindAll(this, 'render', 'unrender', 'remove');
            this.model.bind('change', this.render);
            this.model.bind('remove', this.unrender);
        },
        render : function() {
            var tag_html = typeset_tag(this.model.get('name'));
            this.$el.html(tag_html + ' <i class="icon-remove delete-tag"></i>');
            return this;
        },
        unrender : function() {
            this.$el.remove();
        },
        remove : function() {
            this.model.destroy();
        }
    });

    teoremer.TagListView = Backbone.View.extend({
        events: {},
        initialize: function() {
            _.bindAll(this, 'render', 'addItem', 'appendItem', 'keyPress', 'getTagList');
            this.collection = new teoremer.TagList();
            this.collection.bind('add', this.appendItem);
            this.events['click #' + this.options.prefix + '-tag-add'] = 'addItem';
            this.events['keypress #' + this.options.prefix + '-tag-name'] = 'keyPress';
            this.render();
            this.input_field = this.$('#' + this.options.prefix + '-tag-name');
            this.input_field.typeahead({
                source : function(query, process) {
                    $.get(api_prefix + 'tags/prefixed/' + query, function(data) {
                        process(data);
                    }, 'json');
                }
            });
        },
        render: function() {
            var self = this;
            var html = Handlebars.templates.tag_list_input({
                prefix: this.options.prefix
            });
            this.$el.html(html);
            _(this.collection.models).each(function(item) {
                self.appendItem(item);
            }, this);
        },
        keyPress: function(e) {
            if (e.keyCode == 13) {
                this.addItem();
            }
        },
        addItem: function() {
            var value = this.input_field.val();
            if (value) {
                this.input_field.val('');
                var item = new teoremer.TagItem({
                    name: value
                });
                this.collection.add(item);
                MathJax.Hub.Queue(["Typeset", MathJax.Hub, item.$el]);
            }
        },
        appendItem: function(item) {
            var tagItemView = new teoremer.TagItemView({
                model: item
            });
            this.$('#' + this.options.prefix + '-tag-list').append(tagItemView.render().el);
        },
        getTagList: function() {
            return this.collection.map(function(item) { return item.get('name'); });
        }
    });

    teoremer.SearchItem = Backbone.Model.extend({
    });

    teoremer.SearchList = Backbone.Collection.extend({
        has_more: false,
        initialize: function() {
            _.bindAll(this, 'parse');
        },
        model: teoremer.SearchItem,
        url: api_prefix + 'items',
        parse: function(response) {
            this.has_more = response.meta.has_more
            return response.items;
        }
    });

    teoremer.SearchItemView = Backbone.View.extend({
        tagName: 'tr',
        initialize: function() {
            _.bindAll(this, 'render');
            this.model.bind('change', this.render);
        },
        render: function() {
            var tags = this.model.get('tags');
            var context = {
                'id':           this.model.get('id'),
                'itemname':     capitalize(type_short_to_long(this.model.get('type'))) + ' ' + this.model.get('id'),
                'pritags':      _.map(tags.primary, typeset_tag).join(', '),
                'sectags':      _.map(tags.secondary, typeset_tag),
                'author':       { 'name': 'Jan Marthedal Rasmussen' },
                'published_at': '2013-04-04 12:54:12'
            }
            var html = Handlebars.templates.search_list_item(context);
            this.$el.html(html);
            return this;
        }
    });

    teoremer.SearchListView = Backbone.View.extend({
        includeTags: [],
        excludeTags: [],
        events: {
            'click .search-list-more': 'fetchMore'
        },
        initialize: function() {
            _.bindAll(this, 'render', 'appendItem', 'setIncludeTags', 'setExcludeTags', 'fetchMore');
            this.collection = new teoremer.SearchList();
            this.collection.bind('reset', this.render);
            this.collection.bind('add', this.appendItem);
            this.render();
        },
        showHideMoreButton: function() {
            if (this.collection.has_more) {
                this.$('.search-list-more').show();
            } else {
                this.$('.search-list-more').hide();
            }
        },
        render: function() {
            var html = Handlebars.templates.search_list_container({});
            this.$el.html(html);
            var self = this;
            _(this.collection.models).each(function(item) {
                self.appendItem(item);
            }, this);
            this.showHideMoreButton();
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, this.el]);
        },
        appendItem: function(item) {
            var searchItemView = new teoremer.SearchItemView({
                model: item
            });
            this.$('tbody').append(searchItemView.render().el);
        },
        doFetch: function(reset) {
            var options = {};
            options.data = {
                type:   this.options.itemtype,
                intags: JSON.stringify(this.includeTags),
                extags: JSON.stringify(this.excludeTags)
            };
            if (reset) {
                options.reset = true;
                options.data.offset = 0;
            } else {
                var self = this;
                options.remove = false;
                options.data.offset = this.collection.length;
                options.success = function() { self.showHideMoreButton(); };
            }
            this.collection.fetch(options);
        },
        fetchMore: function() {
            this.doFetch(false);
        },
        setIncludeTags: function(tag_list) {
            this.includeTags = tag_list;
            this.doFetch(true);
        },
        setExcludeTags: function(tag_list) {
            this.excludeTags = tag_list;
            this.doFetch(true);
        }
    });

    window.teoremer = teoremer;

})(window);
