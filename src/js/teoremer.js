(function(window) {

    var $ = window.jQuery;

    var api_prefix = '/api/';

    var teoremer = {};

    teoremer.setupCsrf = function() {
        var csrftoken = $.cookie('csrftoken');

        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        $.ajaxSetup({
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    };

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
        return _.map(tag_list, typeset_tag);
    }

    function type_short_to_long(st) {
        switch (st.toUpperCase()) {
            case 'D':
                return 'definition';
            case 'T':
                return 'theorem';
            case 'P':
                return 'proof';
        }
    }

    function capitalize(st) {
        return st.charAt(0).toUpperCase() + st.slice(1);
    }

    function reverse_view_redirect(view, arg1) {
        var url;
        if (view == 'drafts.views.show') {
            url = '/draft/' + arg1;
        } else if (view == 'items.views.show_final') {
            url = '/item/' + arg1;
        } else {
            console.log('Cannot do reverse lookup for view ' + view);
            return;
        }
        window.location.href = url;
    }

    /***************************
     * Models and collections
     ***************************/

    // private

    var TagItem = Backbone.Model.extend({
        // name
        typeset: function() {
            return typeset_tag(this.get('name'));
        },
        toJSON: function() {
            return this.get('name');
        },
        parse: function(resp) {
            return { name: resp };
        }
    });

    var TagList = Backbone.Collection.extend({
        model: TagItem,
        parse: function(resp) {
            return _.map(resp, function(item) {
                return new TagItem(item, { parse: true });
            });
        }
    });

    var Category = Backbone.Model.extend({
        // tag_list
        typeset: function() {
            return Handlebars.templates.tag_list({
                tags: this.get('tag_list').map(function(tag_item) {
                    return tag_item.typeset();
                })
            });
        },
        toJSON: function() {
            return this.get('tag_list').map(function(tag_item) {
                return tag_item.toJSON();
            });
        },
        parse: function(resp) {
            return {
                tag_list: new TagList(resp, { parse: true })
            };
        }
    });

    var CategoryList = Backbone.Collection.extend({
        model: Category,
        parse: function(resp) {
            return _.map(resp, function(item) {
                return new Category(item, { parse: true });
            });
        }
    });

    var TagAssociation = Backbone.Model.extend({
        toJSON: function() {
            return {
                tag: this.get('tag').toJSON(),
                category: this.get('category').toJSON()
            };
        },
        parse: function(resp) {
            return {
                tag: new TagItem(resp.tag, { parse: true }),
                category: new Category(resp.category, { parse: true })
            };
        }
    });

    var TagAssociationList = Backbone.Collection.extend({
       model: TagAssociation,
       parse: function(resp) {
            return _.map(resp, function(item) {
                return new TagAssociation(item, { parse: true });
            });
       }
    });

    var MathItem = Backbone.Model;

    var TopList = Backbone.Collection.extend({
        model: MathItem,
        url: api_prefix + 'items',
        parse: function(response) {
            return response.items;
        }
    });

    var SearchList = Backbone.Collection.extend({
        has_more: false,
        initialize: function() {
            _.bindAll(this, 'parse');
        },
        model: MathItem,
        url: api_prefix + 'items',
        parse: function(response) {
            this.has_more = response.meta.has_more;
            return response.items;
        }
    });

    // public

    teoremer.DraftItem = Backbone.Model.extend({
        urlRoot: '/api/drafts',
        parse: function(resp) {
            var parsed = {
                body:    resp.body,
                pricats: new CategoryList(resp.pricats, { parse: true }),
                seccats: new CategoryList(resp.seccats, { parse: true })
            };
            if ('id' in resp) {                // updating
                parsed.id = resp.id;
            } else {                           // new
                parsed.type = resp.type;
                if ('parent' in resp) {
                    parsed.parent = resp.parent;
                }
            }
            return parsed;
        }
    });

    teoremer.FinalItem = Backbone.Model.extend({
        urlRoot: '/api/final',
        parse: function(resp) {
            return {
                id:        resp.id,
                pricats:   new CategoryList(resp.pricats, { parse: true }),
                seccats:   new CategoryList(resp.seccats, { parse: true }),
                tagcatmap: new TagAssociationList(resp.tagcatmap, { parse: true })
            };
        }
    });

    teoremer.SearchTerms = Backbone.Model.extend({
        defaults: {
            status: 'F'
        },
        toJSON: function() {
            var data = _.clone(this.attributes);
            data.intags = JSON.stringify(data.includeTags);
            data.extags = JSON.stringify(data.excludeTags);
            delete data.includeTags;
            delete data.excludeTags;
            return data;
        }
    });

    teoremer.SourceItem = Backbone.Model.extend({
        defaults: {
            type: 'book',
            author: [''],
            editor: [''],
            publisher: 'Some publisher'
        }
    });

    /***************************
     * Views
     ***************************/

    var RemovableTagView = Backbone.View.extend({
        tagName: 'span',
        className: 'tag',
        events: {
            'click .delete-tag': 'remove'
        },
        initialize: function() {
            _.bindAll(this, 'render', 'unrender', 'remove');
            this.model.on('change', this.render);
            this.model.on('remove', this.unrender);
        },
        render: function() {
            var tag_html = this.model.typeset();
            this.$el.html(tag_html + ' <i class="icon-remove delete-tag"></i>');
            return this;
        },
        unrender: function() {
            this.$el.remove();
        },
        remove: function() {
            this.model.destroy();
        }
    });

    teoremer.TagListView = Backbone.View.extend({
        // standard
        events: function() {
            var e = {};
            e['click #tag-add-' + this.uid] = 'addItem';
            e['keypress #tag-name-' + this.uid] = 'keyPress';
            return e;
        },
        initialize: function() {
            _.bindAll(this, 'render', 'addItem', 'addOne', 'keyPress', 'getTagList', 'events');
            this.uid = _.uniqueId();
            this.collection = new TagList();
            this.collection.bind('add', this.addOne);
            this.render();
            this.input_field = this.$('#tag-name-' + this.uid);
            this.input_field.typeahead({
                source: function(query, process) {
                    $.get(api_prefix + 'tags/prefixed/' + query, function(data) {
                        process(data);
                    }, 'json');
                }
            });
        },
        render: function() {
            var html = Handlebars.templates.tag_list_input({
                uid: this.uid
            });
            this.$el.html(html);
            this.collection.each(this.addOne);
        },
        // helpers
        keyPress: function(e) {
            if (e.keyCode == 13) {
                this.addItem();
            }
        },
        addItem: function() {
            var value = this.input_field.val();
            if (value) {
                this.input_field.val('');
                var item = new TagItem({
                    name: value
                });
                this.collection.add(item);
            }
        },
        addOne: function(item) {
            var removableTagView = new RemovableTagView({
                model: item
            });
            this.$('#tag-list-' + this.uid).append(removableTagView.render().el);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, removableTagView.$el.get()]);
        },
        // public methods
        getTagList: function() {
            return this.collection.map(function(item) {
                return item.get('name');
            });
        }
    });

    teoremer.MathItemView = Backbone.View.extend({
        tagName: 'tr',
        initialize: function() {
            _.bindAll(this, 'render');
            this.model.bind('change', this.render);
        },
        render: function() {
            var categories = this.model.get('categories');
            var html = Handlebars.templates.search_list_item({
                id:          this.model.get('id'),
                item_name:   capitalize(type_short_to_long(this.model.get('type'))) + ' ' + this.model.get('id'),
                item_link:   this.model.get('item_link'),
                pritags:     _.map(_.map(categories.primary, _.last), typeset_tag).join(', '),
                sectags:     _.map(categories.secondary, typeset_tag_list),
                author_name: this.model.get('author'),
                author_link: this.model.get('author_link'),
                timestamp:   this.model.get('timestamp')
            });
            this.$el.html(html);
            return this;
        }
    });

    teoremer.SearchListView = Backbone.View.extend({
        events: {
            'click .search-list-more':   function() { this.doFetch(true); },
            'click .select-final':       function() { this.options.parameters.set('status', 'F'); },
            'click .select-review':      function() { this.options.parameters.set('status', 'R'); },
            'click .select-draft':       function() { this.options.parameters.set('status', 'D'); },
            'click .select-definitions': function() { this.options.parameters.set('type', 'D'); },
            'click .select-theorems':    function() { this.options.parameters.set('type', 'T'); },
            'click .select-proofs':      function() { this.options.parameters.set('type', 'P'); }
        },
        initialize: function() {
            _.bindAll(this, 'render', 'addOne', 'doFetch', 'fetchReset');
            this.collection = new SearchList();
            this.collection.on('reset', this.render);
            this.collection.on('add', this.addOne);
            this.options.parameters.set('type', this.options.itemtypes.charAt(0));
            this.options.parameters.on('change', this.fetchReset, this);
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
            var status = this.options.parameters.get('status');
            var type = this.options.parameters.get('type');
            var html = Handlebars.templates.search_list_container({
                enable_drafts:      !!this.options.enable_drafts,
                status_final:       status == 'F',
                status_review:      status == 'R',
                status_draft:       status == 'D',
                enable_definitions: this.options.itemtypes.indexOf('D') != -1,
                enable_theorems:    this.options.itemtypes.indexOf('T') != -1,
                enable_proofs:      this.options.itemtypes.indexOf('P') != -1,
                type_definition:    type == 'D',
                type_theorem:       type == 'T',
                type_proof:         type == 'P'
            });
            this.$el.html(html);
            this.collection.each(this.addOne);
            this.postAppend();
        },
        addOne: function(item) {
            var mathItemView = new teoremer.MathItemView({
                model: item
            });
            this.$('tbody').append(mathItemView.render().el);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, mathItemView.$el.get()]);
        },
        doFetch: function(append) {
            var options = {};
            options.data = this.options.parameters.toJSON();
            if (append) {
                var self = this;
                options.remove = false;
                options.data.offset = this.collection.length;
                options.success = function() {
                    self.postAppend();
                };
            } else {
                options.reset = true;
                options.data.offset = 0;
            }
            this.collection.fetch(options);
        },
        fetchReset: function() {
            this.doFetch(false);
        }
    });

    teoremer.TopListView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render', 'addOne');
            this.collection = new TopList();
            this.collection.on('reset', this.render);
            this.collection.on('add', this.addOne);
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
            this.$('tbody').append(mathItemView.render().el);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, mathItemView.$el.get()]);
        }
    });

    teoremer.BodyEditView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');
            var self = this;
            this.$el.on('input propertychange', function() {
                self.model.set('body', this.value);
            });
            this.render();
        },
        render: function() {
            this.$el.val(this.model.get('body'));
            return this;
        }
    });

    teoremer.BodyPreviewView = Backbone.View.extend({
        initialize: function() {
            this.converter = new Showdown.converter();
            this.model.on('change:body', this.render, this);
            this.render.call(this);
        },
        render: function() {
            var source = this.model.get('body');
            var insertsCounter = 0, mathInserts = {}, inserts = {}, key;
            var pars = source.split('$$');
            for (var i = 0; i < pars.length; i++) {
                if (i % 2) {
                    key = 'zZ' + (++insertsCounter) + 'Zz';
                    mathInserts[key] = '\\[' + pars[i] + '\\]';
                    pars[i] = key;
                } else {
                    pars2 = pars[i].split('$');
                    for (var j = 0; j < pars2.length; j++) {
                        if (j % 2) {
                            key = 'zZ' + (++insertsCounter) + 'Zz';
                            mathInserts[key] = '\\(' + pars2[j] + '\\)';
                            pars2[j] = key;
                        }
                    }
                    pars[i] = pars2.join('');
                }
            }
            source = pars.join('');
            // [text#tag] or [#tag]
            source = source.replace(/\[([^#\]]*)#([\w -]+)\]/g, function(full_match, text, tag) {
                text = text || tag;
                key = 'zZ' + (++insertsCounter) + 'Zz';
                inserts[key] = '<a href="#" rel="tooltip" data-original-title="tag: ' + tag + '"><i>' + text + '</i></a>';
                return key;
            });
            // [@q25tY]
            source = source.replace(/\[([^@\]]*)@(\w+)\]/g, function(full_match, text, item_id) {
                text = text || item_id;
                key = 'zZ' + (++insertsCounter) + 'Zz';
                inserts[key] = '<a href="#" rel="tooltip" data-original-title="item: ' + item_id + '"><b>' + text + '</b></a>';
                return key;
            });
            // disable markdown links and images
            source = source.replace("[", "&#91;").replace("]", "&#93;").replace("<", "&lt;").replace(">", "&gt;");
            var html = this.converter.makeHtml(source);
            for (key in inserts) {
                html = html.replace(key, inserts[key]);
            }
            for (key in mathInserts) {
                html = html.replace(key, mathInserts[key]);
            }
            this.$el.html(html);
            this.$el.tooltip({
                selector: "a[rel=tooltip]"
            });
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, this.$el.get()]);
        }
    });

    teoremer.SaveDraftView = Backbone.View.extend({
        events: {
            'click': 'save'
        },
        initialize: function() {
            _.bindAll(this, 'save');
        },
        save: function() {
            this.model.save(null, {
                wait: true,
                success: function(model, response) {
                    reverse_view_redirect('drafts.views.show', model.get('id'));
                },
                error: function(model, error) {
                    console.log(model.toJSON());
                    console.log('error saving');
                }
            });
        }
    });

    teoremer.AddCategoryView = Backbone.View.extend({
        // standard
        el: $('#modal-container'),
        events: {
            'click    .cancel': 'remove',
            'click    .btn-primary': 'addAction',
            'click    #category-minus-btn': 'minusAction',
            'click    #category-plus-btn': 'plusAction',
            'keypress input': 'keyPress'
        },
        initialize: function() {
            _.bindAll(this, 'render', 'renderTags', 'keyPress', 'addAction', 'minusAction', 'plusAction');
            this.collection = new TagList();
            this.collection.on('add remove', this.renderTags);
            this.render();
            this.setElement(this.$('.modal'));
            // so 'this.remove' functions correctly
            this.$el.modal({
                'backdrop': false,
                'show': true
            });
            this.input_element = this.$('input');
            this.input_element.focus();
        },
        render: function() {
            var html = Handlebars.templates.add_category();
            this.$el.html(html);
        },
        // helpers
        renderTags: function() {
            var html = Handlebars.templates.tag_list({
                tags: this.collection.map(function(model) {
                    return model.typeset();
                })
            });
            this.$('div.category').html(html);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, this.$el.get()]);
        },
        keyPress: function(e) {
            if (e.keyCode == 13) {
                if (this.input_element.val()) {
                    this.plusAction();
                } else {
                    this.addAction();
                }
            }
        },
        addAction: function() {
            this.options.add(new Category({
                tag_list: this.collection
            }));
            this.remove();
        },
        minusAction: function() {
            if (!this.input_element.val()) {
                this.collection.pop();
            }
            this.input_element.val('').focus();
        },
        plusAction: function() {
            var value = this.input_element.val();
            if (value) {
                this.collection.push({
                    name: value
                });
            }
            this.input_element.val('').focus();
        }
    });

    var RemovableCategoryView = Backbone.View.extend({
        tagName: 'span',
        className: 'category',
        events: {
            'click .delete-category': 'remove'
        },
        initialize: function() {
            _.bindAll(this, 'render', 'unrender', 'remove');
            this.model.on('change', this.render);
            this.model.on('remove', this.unrender);
        },
        render: function() {
            var tag_html = this.model.typeset();
            this.$el.html(tag_html + ' <i class="icon-remove delete-category"></i>');
            return this;
        },
        unrender: function() {
            this.$el.remove();
        },
        remove: function() {
            this.model.destroy();
        }
    });

    teoremer.EditableCategoryListView = Backbone.View.extend({
        // standard
        events: function() {
            var e = {};
            e['click #category-add-' + this.uid] = '_promptCategory';
            return e;
        },
        initialize: function() {
            _.bindAll(this, 'render', '_addOne', '_promptCategory');
            this.uid = _.uniqueId();
            this.collection.bind('add', this._addOne);
            this.render();
        },
        render: function() {
            var html = Handlebars.templates.editable_category_list({
                uid: this.uid
            });
            this.$el.html(html);
            this.collection.each(this._addOne);
        },
        // helpers
        _addOne: function(item) {
            var categoryView = new RemovableCategoryView({
                model: item
            });
            this.$('#category-list-' + this.uid).append(categoryView.render().el);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, categoryView.$el.get()]);
        },
        _promptCategory: function() {
            var self = this;
            new teoremer.AddCategoryView({
                add: function(category) {
                    self.collection.add(category);
                }
            });
        }
    });

    var ChangableTagAssociation = Backbone.View.extend({
        // standard
        tagName: 'tr',
        events: {
            'click button': '_change'
        },
        initialize: function() {
            _.bindAll(this, 'render', '_change');
            this.model.on('change', this.render);
        },
        render: function() {
            var html = Handlebars.templates.tag_association({
                tag: this.model.get('tag').typeset(),
                category: this.model.get('category').typeset()
            });
            this.$el.html(html);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, this.$el.get()]);
            return this;
        },
        // helpers
        _change: function() {
            var self = this;
            new teoremer.AddCategoryView({
                add: function(category) {
                    self.model.set('category', category);
                }
            });
        }
    });

    teoremer.ChangableTagAssociationListView = Backbone.View.extend({
        // standard
        initialize: function() {
            _.bindAll(this, 'render', '_addOne');
            this.collection.bind('add', this._addOne);
            this.render();
        },
        render: function() {
            var html = Handlebars.templates.tag_association_list();
            this.$el.html(html);
            this.collection.each(this._addOne);
        },
        // helpers
        _addOne: function(item) {
            var tagAssociation = new ChangableTagAssociation({
                model: item
            });
            this.$('tbody').append(tagAssociation.render().el);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, tagAssociation.$el.get()]);
        }
    });

    teoremer.SaveFinalView = Backbone.View.extend({
        events: {
            'click': 'save'
        },
        initialize: function() {
            _.bindAll(this, 'save');
        },
        save: function() {
            this.model.save(null, {
                wait: true,
                success: function(model, response) {
                    reverse_view_redirect('items.views.show_final', model.get('id'));
                },
                error: function(model, error) {
                    console.log(model.toJSON());
                    console.log('error saving');
                }
            });
        }
    });

    var SourceEditView = Backbone.View.extend({
        tagName: 'div',
        className: 'form-horizontal',
        initialize: function() {
            _.bindAll(this, 'render', '_updateModel');
            this.$el.on('input propertychange', this._updateModel);
            this.render();
        },
        _updateModel: function() {
            var view = this, key, value;
            view.$('input').each(function() {
                key = $(this).attr('id').slice(5).toLowerCase();
                if (key.match(/^[a-z]+$/)) {
                    value = $(this).val();
                    value ? view.model.set(key, value) : view.model.unset(key);
                } else if (key.match(/^[a-z]+0$/)) {
                    key = key.slice(0, -1);
                    var idBase = '#input' + capitalize(key);
                    value = [];
                    for (var j=0;; j++) {
                        var elem = $(idBase + j), v;
                        if (!elem.length)
                            break;
                        v = elem.val();
                        if (v)
                            value.push(v);
                    }
                    value.length ? view.model.set(key, value) : view.model.unset(key);
                } 
            });
        }
    });

    teoremer.BookSourceEditView = SourceEditView.extend({
        render: function() {
            var html = Handlebars.templates.book_source_edit(this.model.attributes);
            this.$el.html(html);
        }
    });

    teoremer.ArticleSourceEditView = SourceEditView.extend({
        render: function() {
            var html = Handlebars.templates.article_source_edit(this.model.attributes);
            this.$el.html(html);
        }
    });

    teoremer.SourceRenderView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');
            this.model.on('change', this.render);
            this.render();
        },
        render: function() {
            var html = Handlebars.templates.render_source({'data': this.model.attributes});
            this.$el.html(html);
        }
    });

    window.teoremer = teoremer;

})(window);
