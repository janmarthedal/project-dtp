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

    function typeset_tag_list(tag_list) {
        return _.map(tag_list, typeset_tag)
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

    teoremer.TagItem = Backbone.Model;

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
            _.bindAll(this, 'render', 'addItem', 'addOne', 'keyPress', 'getTagList');
            this.collection = new teoremer.TagList();
            this.collection.bind('add', this.addOne);
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
            var html = Handlebars.templates.tag_list_input({
                prefix: this.options.prefix
            });
            this.$el.html(html);
            this.collection.each(this.addOne);
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
        addOne: function(item) {
            var tagItemView = new teoremer.TagItemView({
                model: item
            });
            this.$('#' + this.options.prefix + '-tag-list').append(tagItemView.render().el);
        },
        getTagList: function() {
            return this.collection.map(function(item) { return item.get('name'); });
        }
    });

    teoremer.MathItem = Backbone.Model;

    teoremer.MathItemView = Backbone.View.extend({
        tagName: 'tr',
        initialize: function() {
            _.bindAll(this, 'render');
            this.model.bind('change', this.render);
        },
        render: function() {
            var categories = this.model.get('categories');
            var context = {
                id:          this.model.get('id'),
                item_name:   capitalize(type_short_to_long(this.model.get('type'))) + ' ' + this.model.get('id'),
                item_link:   this.model.get('item_link'),
                pritags:     _.map(_.map(categories.primary, _.last), typeset_tag).join(', '),
                sectags:     _.map(categories.secondary, typeset_tag_list),
                author_name: this.model.get('author'),
                author_link: this.model.get('author_link'),
                timestamp:   this.model.get('timestamp')
            }
            var html = Handlebars.templates.search_list_item(context);
            this.$el.html(html);
            return this;
        }
    });

    teoremer.SearchList = Backbone.Collection.extend({
        has_more: false,
        initialize: function() {
            _.bindAll(this, 'parse');
        },
        model: teoremer.MathItem,
        url: api_prefix + 'items',
        parse: function(response) {
            this.has_more = response.meta.has_more
            return response.items;
        }
    });

    teoremer.SearchListView = Backbone.View.extend({
        includeTags: [],
        excludeTags: [],
        status: 'F',
        events: {
            'click .search-list-more':   'fetchMore',
            'click .select-final':       'selectFinal',
            'click .select-review':      'selectReview',
            'click .select-draft':       'selectDraft',
            'click .select-definitions': 'selectDefinitions',
            'click .select-theorems':    'selectTheorems',
            'click .select-proofs':      'selectProofs'
        },
        initialize: function() {
            this.itemtype = this.options.itemtypes.charAt(0);
            _.bindAll(this, 'render', 'addOne', 'setIncludeTags', 'setExcludeTags',
                            'fetchMore', 'selectReview', 'selectFinal');
            this.collection = new teoremer.SearchList();
            this.collection.bind('reset', this.render);
            this.collection.bind('add', this.addOne);
            this.render();
        },
        postAppend: function() {
            if (this.collection.has_more) {
                this.$('.search-list-more').show();
            } else {
                this.$('.search-list-more').hide();
            }
        },
        render: function() {
            var html = Handlebars.templates.search_list_container({
                enable_drafts: !!this.options.enable_drafts,
                status_final: this.status == 'F',
                status_review: this.status == 'R',
                status_draft: this.status == 'D',
                enable_definitions: this.options.itemtypes.indexOf('D') != -1,
                enable_theorems: this.options.itemtypes.indexOf('T') != -1,
                enable_proofs: this.options.itemtypes.indexOf('P') != -1,
                type_definition: this.itemtype == 'D',
                type_theorem: this.itemtype == 'T',
                type_proof: this.itemtype == 'P'
            });
            this.$el.html(html);
            this.collection.each(this.addOne);
            this.postAppend();
        },
        addOne: function(item) {
            var mathItemView = new teoremer.MathItemView({
                model: item
            });
            var element = mathItemView.render().el;
            this.$('tbody').append(element);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, element]);
        },
        doFetch: function(reset) {
            var options = {};
            options.data = {
                type:   this.itemtype,
                status: this.status,
                intags: JSON.stringify(this.includeTags),
                extags: JSON.stringify(this.excludeTags)
            };
            if (this.options.user_id) {
                options.data.user = this.options.user_id;
            }
            if (reset) {
                options.reset = true;
                options.data.offset = 0;
            } else {
                var self = this;
                options.remove = false;
                options.data.offset = this.collection.length;
                options.success = function() { self.postAppend(); };
            }
            this.collection.fetch(options);
        },
        fetchMore: function() {
            this.doFetch(false);
        },
        selectFinal: function() {
            this.setStatus('F');
        },
        selectReview: function() {
            this.setStatus('R');
        },
        selectDraft: function() {
            this.setStatus('D');
        },
        selectDefinitions: function() {
            this.setType('D');
        },
        selectTheorems: function() {
            this.setType('T');
        },
        selectProofs: function() {
            this.setType('P');
        },
        setIncludeTags: function(tag_list) {
            this.includeTags = tag_list;
            this.doFetch(true);
        },
        setExcludeTags: function(tag_list) {
            this.excludeTags = tag_list;
            this.doFetch(true);
        },
        setStatus: function(status) {
            if (status != this.status) {
                this.status = status;
                this.doFetch(true);
            }
        },
        setType: function(itemtype) {
            if (itemtype != this.itemtype) {
                this.itemtype = itemtype;
                this.doFetch(true);
            }
        }
    });

    teoremer.TopList = Backbone.Collection.extend({
        model: teoremer.MathItem,
        url: api_prefix + 'items',
        parse: function(response) {
            return response.items;
        }
    });

    teoremer.TopListView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render', 'addOne');
            this.collection = new teoremer.TopList();
            this.collection.bind('reset', this.render);
            this.collection.bind('add', this.addOne);
            this.render();
        },
        render: function() {
            var html = Handlebars.templates.top_list_container();
            this.$el.html(html);
            this.collection.each(this.addOne);
        },
        addOne: function(item) {
            var mathItemView = new teoremer.MathItemView({
                model: item
            });
            var element = mathItemView.render().el;
            this.$('tbody').append(element);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, element]);
        }
    });

    teoremer.BodyPreview = function(el) {
        this.el = el;
        this.converter = new Showdown.converter();
        this.setSource = function(source) {
            var insertsCounter = 0, inserts = {}, key;
            var pars = source.split('$$');
            for (var i=0; i < pars.length; i++) {
                if (i % 2) {
                    insertsCounter++;
                    key = 'zZ' + insertsCounter + 'Zz';
                    inserts[key] = '\\[' + pars[i] + '\\]';
                    pars[i] = key;
                }
            }
            var html = this.converter.makeHtml(pars.join(''));
            for (key in inserts) {
                html = html.replace(key, inserts[key]);
            }
            this.el.html(html);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, this.el.get()]);
        }
    }

    window.teoremer = teoremer;

})(window);
(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['search_list_container'] = template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  var buffer = "", stack1, self=this;

function program1(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n";
  stack1 = helpers['if'].call(depth0, depth0.type_definition, {hash:{},inverse:self.program(4, program4, data),fn:self.program(2, program2, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  }
function program2(depth0,data) {
  
  
  return "\n<span class=\"label label-info\">definitions</span>\n";
  }

function program4(depth0,data) {
  
  
  return "\n<a class=\"select-definitions\" href=\"#\">definitions</a>\n";
  }

function program6(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n";
  stack1 = helpers['if'].call(depth0, depth0.type_theorem, {hash:{},inverse:self.program(9, program9, data),fn:self.program(7, program7, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  }
function program7(depth0,data) {
  
  
  return "\n<span class=\"label label-info\">theorems</span>\n";
  }

function program9(depth0,data) {
  
  
  return "\n<a class=\"select-theorems\" href=\"#\">theorems</a>\n";
  }

function program11(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n";
  stack1 = helpers['if'].call(depth0, depth0.type_proof, {hash:{},inverse:self.program(14, program14, data),fn:self.program(12, program12, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  }
function program12(depth0,data) {
  
  
  return "\n<span class=\"label label-info\">proofs</span>\n";
  }

function program14(depth0,data) {
  
  
  return "\n<a class=\"select-proofs\" href=\"#\">proofs</a>\n";
  }

function program16(depth0,data) {
  
  
  return "\n<span class=\"label label-info\">final</span>\n";
  }

function program18(depth0,data) {
  
  
  return "\n<a class=\"select-final\" href=\"#\">final</a>\n";
  }

function program20(depth0,data) {
  
  
  return "\n<span class=\"label label-info\">review</span>\n";
  }

function program22(depth0,data) {
  
  
  return "\n <a class=\"select-review\" href=\"#\">review</a>\n";
  }

function program24(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n";
  stack1 = helpers['if'].call(depth0, depth0.status_draft, {hash:{},inverse:self.program(27, program27, data),fn:self.program(25, program25, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  }
function program25(depth0,data) {
  
  
  return "\n<span class=\"label label-info\">draft</span>\n";
  }

function program27(depth0,data) {
  
  
  return "\n<a class=\"select-draft\" href=\"#\">draft</a>\n";
  }

  buffer += "<p class=\"pull-right\">\n<span class=\"label label-info\">date</span> <a href=\"#\">points</a>\n</p>\n\n<p>\n";
  stack1 = helpers['if'].call(depth0, depth0.enable_definitions, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  stack1 = helpers['if'].call(depth0, depth0.enable_theorems, {hash:{},inverse:self.noop,fn:self.program(6, program6, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  stack1 = helpers['if'].call(depth0, depth0.enable_proofs, {hash:{},inverse:self.noop,fn:self.program(11, program11, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n|\n";
  stack1 = helpers['if'].call(depth0, depth0.status_final, {hash:{},inverse:self.program(18, program18, data),fn:self.program(16, program16, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  stack1 = helpers['if'].call(depth0, depth0.status_review, {hash:{},inverse:self.program(22, program22, data),fn:self.program(20, program20, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  stack1 = helpers['if'].call(depth0, depth0.enable_drafts, {hash:{},inverse:self.noop,fn:self.program(24, program24, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n</p>\n\n<table class=\"table\">\n<tbody>\n</tbody>\n</table>\n\n<button class=\"btn btn-link pull-right search-list-more\" type=\"button\">Show more</button>\n";
  return buffer;
  });
templates['search_list_item'] = template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

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
  
  var buffer = "", stack1;
  buffer += "<span class=\"category\">";
  stack1 = helpers.each.call(depth0, depth0, {hash:{},inverse:self.noop,fn:self.program(4, program4, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "</span>";
  return buffer;
  }
function program4(depth0,data) {
  
  var buffer = "";
  buffer += "<span class=\"tag\">"
    + escapeExpression((typeof depth0 === functionType ? depth0.apply(depth0) : depth0))
    + "</span>";
  return buffer;
  }

  buffer += "<td>\n<div><a href=\"";
  if (stack1 = helpers.item_link) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.item_link; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">";
  if (stack1 = helpers.item_name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.item_name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1);
  stack1 = helpers['if'].call(depth0, depth0.pritags, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "</a></div>\n<div><small class=\"pull-right\">by <a href=\"";
  if (stack1 = helpers.author_link) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.author_link; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">";
  if (stack1 = helpers.author_name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.author_name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</a> at ";
  if (stack1 = helpers.timestamp) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.timestamp; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</small>\n";
  stack1 = helpers.each.call(depth0, depth0.sectags, {hash:{},inverse:self.noop,fn:self.program(3, program3, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
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
templates['top_list_container'] = template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  


  return "<table class=\"table\">\n<tbody>\n</tbody>\n</table>\n";
  });
})();
