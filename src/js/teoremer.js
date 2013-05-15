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
                MathJax.Hub.Queue(["Typeset", MathJax.Hub, item.$el.get()]);
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
            var mathItem = mathItemView.render();
            this.$('tbody').append(mathItem.el);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, mathItem.$el.get()]);
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
