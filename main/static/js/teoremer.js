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
        model: teoremer.SearchItem,
        url: api_prefix + 'items'
    });

    teoremer.SearchItemView = Backbone.View.extend({
        tagName: 'li',
        initialize: function() {
            _.bindAll(this, 'render');
            this.model.bind('change', this.render);
        },
        render: function() {
            var tags = this.model.get('tags');
            var context = {
                'id':       this.model.get('id'),
                'itemname': capitalize(type_short_to_long(this.model.get('type'))) + ' ' + this.model.get('id'),
                'pritags':  _.map(tags.primary, typeset_tag).join(', '),
                'sectags':  _.map(tags.secondary, typeset_tag)
            }
            var html = Handlebars.templates.search_list_item(context);
            this.$el.html(html);
            return this;
        },
    });

    teoremer.SearchListView = Backbone.View.extend({
        includeTags: [],
        excludeTags: [],
        initialize: function() {
            _.bindAll(this, 'render', 'appendItem', 'refetch', 'setIncludeTags', 'setExcludeTags');
            this.collection = new teoremer.SearchList();
            this.collection.bind('reset', this.render);
            this.render();
        },
        render: function() {
            var self = this;
            this.$el.html('<ul></ul>')
            _(this.collection.models).each(function(item) {
                self.appendItem(item);
            }, this);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, this.el]);
        },
        appendItem: function(item) {
            var searchItemView = new teoremer.SearchItemView({
                model: item
            });
            this.$('ul').append(searchItemView.render().el);
        },
        refetch: function() {
            this.collection.fetch({
                reset: true,
                data: {
                    type:   this.options.itemtype,
                    intags: JSON.stringify(this.includeTags),
                    extags: JSON.stringify(this.excludeTags)
                }
            });
        },
        setIncludeTags: function(tag_list) {
            this.includeTags = tag_list;
            this.refetch();
        },
        setExcludeTags: function(tag_list) {
            this.excludeTags = tag_list;
            this.refetch();
        }
    });

    window.teoremer = teoremer;

})(window);
