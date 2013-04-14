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
                id:          this.model.get('id'),
                item_name:   capitalize(type_short_to_long(this.model.get('type'))) + ' ' + this.model.get('id'),
                item_link:   this.model.get('item_link'),
                pritags:     _.map(tags.primary, typeset_tag).join(', '),
                sectags:     _.map(tags.secondary, typeset_tag),
                author_name: this.model.get('author'),
                author_link: this.model.get('author_link'),
                timestamp:   this.model.get('timestamp')
            }
            var html = Handlebars.templates.search_list_item(context);
            this.$el.html(html);
            return this;
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
            _.bindAll(this, 'render', 'appendItem', 'setIncludeTags', 'setExcludeTags',
                            'fetchMore', 'selectReview', 'selectFinal');
            this.collection = new teoremer.SearchList();
            this.collection.bind('reset', this.render);
            this.collection.bind('add', this.appendItem);
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
            var self = this;
            _(this.collection.models).each(function(item) {
                self.appendItem(item);
            }, this);
            this.postAppend();
        },
        appendItem: function(item) {
            var searchItemView = new teoremer.SearchItemView({
                model: item
            });
            var element = searchItemView.render().el;
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

    window.teoremer = teoremer;

})(window);
