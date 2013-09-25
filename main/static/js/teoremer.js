(function() {

    var api_prefix = '/api/';

    (function() {
        var csrftoken = $.cookie('csrftoken');
        function csrfSafeMethod(method) {
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
    })();

    // http://www.abeautifulsite.net/blog/2010/01/smoothly-scroll-to-an-element-without-a-jquery-plugin/
    function scrollTo(element) {
        $('body').animate({
            scrollTop: element.offset().top
        }, 200);
    }

    var concept_map = (function() {
        var id_to_concept_map = {};
        return {
            insert: function(id, tag_list) {
                id_to_concept_map['' + id] = tag_list;
            },
            from_id: function(id) {
                return id_to_concept_map[id];
            }
        };
    })();

    var showdown_convert = (function() {
        var converter;
        return function(source) {
            converter || (converter = new Showdown.converter());
            return converter.makeHtml(source);
        };
    })();

    function trim(st) {
        return $.trim(st);
    }

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

    function typeset_category_id(id) {
        var tag_list = concept_map.from_id(id);
        var category = Handlebars.templates.tag_list({
                           tags: typeset_tag_list(tag_list)
                       });
        return '<span class="category">' + category + '</span>';
    }

    function typeset_body(source, typeset_tag, typeset_item) {
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
            inserts[key] = typeset_tag(text, tag);
            return key;
        });
        // [@q25tY]
        source = source.replace(/\[([^@\]]*)@(\w+)\]/g, function(full_match, text, item_id) {
            text = text || item_id;
            key = 'zZ' + (++insertsCounter) + 'Zz';
            inserts[key] = typeset_item(text, item_id);
            return key;
        });
        // disable markdown links and images
        source = source.replace("[", "&#91;").replace("]", "&#93;").replace("<", "&lt;").replace(">", "&gt;");
        var html = showdown_convert(source);
        for (key in inserts) {
            html = html.replace(key, inserts[key]);
        }
        for (key in mathInserts) {
            html = html.replace(key, mathInserts[key]);
        }
        return html;
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

    var to_url = {
        drafts_show: function(arg1) {
            return '/draft/' + arg1;
        },
        items_show_final: function(item) {
            return '/item/' + item;
        },
        source_index: function() {
            return '/source/list';
        },
        source_item: function(id) {
            return '/source/id/' + id;
        },
        sources_add_location_for_item: function(item, source) {
            return '/item/' + item + '/add-validation/' + source;
        },
        sources_add_location_for_draft: function(item, source) {
            return '/draft/' + item + '/add-validation/' + source;
        }
    };

    function redirect(url) {
        window.location.href = url;
    }

    function cleanValues(attrs, escape) {
        var data = {};
        _.each(attrs, function(value, key) {
            if (_.isArray(value)) {
                var v = _.compact(_.map(value, trim));
                if (v.length)
                    data[key] = escape ? _.map(v, _.escape): v;
            } else if (_.isString(value)) {
                var v = trim(value);
                if (v)
                    data[key] = escape ? _.escape(v): v;
            }
        });
        return data;
    }

    function typeset_source(attrs) {
        var data = cleanValues(attrs, true), ret = '', type = data.type, items;
        if (_.size(data) <= 1) {
            return '<i>(empty)</i>';
        }
        // author
        if (data.author) {
            if (data.author.length === 1) {
                ret += _.first(data.author);
            } else if (data.author.length === 2) {
                ret += _.first(data.author) + ' and ' + _.last(data.author);
            } else {
                ret += _.initial(data.author).join(', ') + ', and ' + _.last(data.author);
            }
            ret += '. ';
        }
        // title
        if (data.title) {
            ret += '<i>' + data.title + '</i>. ';
        }
        if (type == 'book') {
            // edition
            if (data.edition) {
                ret += data.edition + ' edition. ';
            }
            // series, volume, number
            items = [];
            if (data.series)
                items.push(data.series);
            if (data.volume)
                items.push('Volume ' + data.volume);
            if (data.number)
                items.push('Number ' + data.number);
            if (items.length) {
                ret += items.join(', ') + '. ';
            }
            // publisher, address, month, year
            items = _.compact([data.publisher, data.address, data.month, data.year]);
            if (items.length) {
                ret += items.join(', ') + '. ';
            }
            // isbn
            items = _.compact([data.isbn10, data.isbn13]);
            if (items.length) {
                ret += 'ISBN: ' + items.join(', ') + '. ';
            }
        }
        // note
        if (data.note) {
            ret += data.note + '.';
        }
        return ret;
    }

    /***************************
     * Modal wrapper
     ***************************/

    var ModalWrapperView = Backbone.View.extend({
        events: function() {
            var self = this;
            var e = {
                'click .close': function() {
                    self.dispatcher.trigger('close');
                },
                'hidden.bs.modal .modal': function() {
                    self.options.innerView.remove();
                    self.remove();
                }
            };
            _.each(this.buttons, function(item) {
                e['click #' + item.id] = function() {
                    self.dispatcher.trigger(item.signal);
                };
            });
            return e;
        },
        initialize: function() {
            _.bindAll(this, 'render', 'close', 'events');
            this.buttons = _.map(this.options.buttons, function (item) {
                return {
                    name: item.name,
                    id: _.uniqueId('modal-'),
                    signal: item.signal || item.name.toLowerCase(),
                    'class': item.primary ? 'btn-primary' : 'btn-default'
                };
            });
            this.dispatcher = _.clone(Backbone.Events);
            this.listenTo(this.dispatcher, 'close', this.close);
            this.render();
            this.$('.modal').modal('show');
            this.options.innerView.modalReady(this.dispatcher);
        },
        render: function() {
            this.$el.html(Handlebars.templates.modal_wrapper({
                title: this.options.title,
                buttons: this.buttons
            }));
            this.$('.modal-body').html(this.options.innerView.render().el);
        },
        close: function() {
            this.$('.modal').modal('hide');
        }
    });

    function show_modal(title, view, buttons) {
        var id = _.uniqueId('model-container-');
        jQuery('<div/>', { id: id }).appendTo('body');
        new ModalWrapperView({
            el: $('#' + id),
            title: title,
            buttons: buttons,
            innerView: view
        });
    }

    /***************************
     * Models and collections
     ***************************/

    var TagItem = Backbone.Model.extend({
        // name
        typeset: function() {
            return typeset_tag(this.get('name'));
        },
        toJSON: function() {
            return this.get('name');
        },
        parse: function(resp) {
            return {
                name: resp
            };
        }
    });

    var TagList = Backbone.Collection.extend({
        model: TagItem,
        parse: function(resp) {
            return _.map(resp, function(item) {
                return new TagItem(item, {
                    parse: true
                });
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
                tag_list: new TagList(resp, {
                    parse: true
                })
            };
        }
    });

    var CategoryList = Backbone.Collection.extend({
        model: Category,
        parse: function(resp) {
            return _.map(resp, function(item) {
                return new Category(item, {
                    parse: true
                });
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
                tag: new TagItem(resp.tag, {
                    parse: true
                }),
                category: new Category(resp.category, {
                    parse: true
                })
            };
        }
    });

    var TagAssociationList = Backbone.Collection.extend({
        model: TagAssociation,
        parse: function(resp) {
            return _.map(resp, function(item) {
                return new TagAssociation(item, {
                    parse: true
                });
            });
        }
    });

    var MathItem = Backbone.Model;

    var TopList = Backbone.Collection.extend({
        model: MathItem,
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
        url: api_prefix + 'item/search',
        parse: function(response) {
            this.has_more = response.meta.has_more;
            return response.items;
        }
    });

    var DraftItem = Backbone.Model.extend({
        defaults: {
          body: '',
          pricats: [],
          seccats: []
        },
        urlRoot: api_prefix + 'draft/',
        parse: function(resp) {
            var parsed = {
                body: resp.body,
                pricats: new CategoryList(resp.pricats, {
                    parse: true
                }),
                seccats: new CategoryList(resp.seccats, {
                    parse: true
                })
            };
            if ('id' in resp) {// updating
                parsed.id = resp.id;
            } else {// new
                parsed.type = resp.type;
                if ('parent' in resp) {
                    parsed.parent = resp.parent;
                }
            }
            return parsed;
        }
    });

    var FinalItem = Backbone.Model.extend({
        urlRoot: api_prefix + 'item/',
        parse: function(resp) {
            return {
                id: resp.id,
                pricats: new CategoryList(resp.pricats, {
                    parse: true
                }),
                seccats: new CategoryList(resp.seccats, {
                    parse: true
                }),
                tagcatmap: new TagAssociationList(resp.tagcatmap, {
                    parse: true
                })
            };
        }
    });

    var SearchTerms = Backbone.Model.extend({
        defaults: {
            status: 'F',
            includeTags: [],
            excludeTags: []
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

    var SourceItem = Backbone.Model.extend({
        urlRoot: api_prefix + 'source/',
        defaults: {
            type: 'book'
        }
    });

    var ValidationItem = Backbone.Model;

    var ValidationList = Backbone.Collection.extend({
        model: ValidationItem
    });

    var SourceList = Backbone.Collection.extend({
        model: SourceItem
    });

    var DocumentModel = Backbone.Model.extend({
        urlRoot: api_prefix + 'document'
    });

    var DocumentEntry = Backbone.Model;

    var DocumentItemList = Backbone.Collection.extend({
        url: api_prefix + 'document/',
        model: DocumentEntry,
        parse: function(response) {
            _.each(response.concept_map, function(elem) {
                concept_map.insert(elem[0], elem[1]);
            });
            return response.items;
        }
    });

    /***************************
     * Views
     ***************************/

    var RemovableTagView = Backbone.View.extend({
        tagName: 'span',
        className: 'tag',
        events: {
            'click .delete-tag': function() {
                this.model.destroy();
            }
        },
        initialize: function() {
            _.bindAll(this, 'render');
            this.listenTo(this.model, 'change', this.render);
            this.listenTo(this.model, 'remove', this.remove);
        },
        render: function() {
            var tag_html = this.model.typeset();
            this.$el.html(tag_html + ' <a href="#" class="glyphicon glyphicon-remove delete-tag"></a>');
            return this;
        }
    });

    var TagListView = Backbone.View.extend({
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
            this.listenTo(this.collection, 'add', this.addOne);
            this.render();
            this.input_field = this.$('#tag-name-' + this.uid);
            /*this.input_field.typeahead({
             source: function(query, process) {
             $.get(api_prefix + 'tags/prefixed/' + query, function(data) {
             process(data);
             }, 'json');
             }
             });*/
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
            if (e.which == 13) {
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

    var MathItemView = Backbone.View.extend({
        tagName: 'li',
        className: 'list-group-item clearfix',
        initialize: function() {
            _.bindAll(this, 'render');
            this.model.bind('change', this.render);
        },
        render: function() {
            var categories = this.model.get('categories');
            var name = capitalize(type_short_to_long(this.model.get('type'))) + ' ' + this.model.get('id');
            if (this.model.has('parent')) {
                var parent = this.model.get('parent');
                name += ' of ' + capitalize(type_short_to_long(parent.type)) + ' ' + parent.id;
            }
            var html = Handlebars.templates.search_list_item({
                id:          this.model.get('id'),
                item_name:   name,
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

    var SearchListView = Backbone.View.extend({
        events: {
            'click .search-list-more': function() {
                this.doFetch(true);
            },
            'click .select-final': function() {
                this.options.parameters.set('status', 'F');
            },
            'click .select-review': function() {
                this.options.parameters.set('status', 'R');
            },
            'click .select-draft': function() {
                this.options.parameters.set('status', 'D');
            },
            'click .select-definitions': function() {
                this.options.parameters.set('type', 'D');
            },
            'click .select-theorems': function() {
                this.options.parameters.set('type', 'T');
            },
            'click .select-proofs': function() {
                this.options.parameters.set('type', 'P');
            }
        },
        initialize: function() {
            _.bindAll(this, 'render', 'addOne', 'doFetch', 'fetchReset');
            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.addOne);
            this.options.parameters.set('type', this.options.itemtypes.charAt(0));
            this.listenTo(this.options.parameters, 'change', this.fetchReset);
            this.render();
        },
        postAppend: function() {
            this.$('.search-list-more').toggle(this.collection.has_more);
        },
        render: function() {
            var status = this.options.parameters.get('status');
            var type = this.options.parameters.get('type');
            var html = Handlebars.templates.search_list_container({
                enable_definitions: this.options.itemtypes.indexOf('D') != -1,
                enable_theorems:    this.options.itemtypes.indexOf('T') != -1,
                enable_proofs:      this.options.itemtypes.indexOf('P') != -1,
                type_definition:    type == 'D',
                type_theorem:       type == 'T',
                type_proof:         type == 'P',
                status_final:       status == 'F',
                status_review:      status == 'R',
                status_draft:       status == 'D',
                enable_drafts:      this.options.statuses.indexOf('D') != -1
            });
            this.$el.html(html);
            this.collection.each(this.addOne);
            this.postAppend();
        },
        addOne: function(item) {
            var mathItemView = new MathItemView({
                model: item
            });
            this.$('ul').append(mathItemView.render().el);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, mathItemView.$el.get()]);
        },
        doFetch: function(append) {
            var status = this.options.parameters.get('status');
            var options = {};
            options.data = this.options.parameters.toJSON();
            if (this.options.restrict && (this.options.restrict.statuses.indexOf(status) != -1)) {
                options.data.user = this.options.restrict.user;
            }
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

    var TopListView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render', 'addOne');
            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.addOne);
            this.render();
        },
        render: function() {
            var html = Handlebars.templates.top_list_container();
            this.$el.html(html);
            this.collection.each(this.addOne);
        },
        addOne: function(item) {
            var mathItemView = new MathItemView({
                model: item
            });
            this.$('tbody').append(mathItemView.render().el);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, mathItemView.$el.get()]);
        }
    });

    var BodyEditView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');
            var self = this;
            this.listenTo(this.$el, 'input propertychange', function() {
                self.model.set('body', this.value);
            });
            this.render();
        },
        render: function() {
            this.$el.val(this.model.get('body'));
            return this;
        }
    });

    var BodyPreviewView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');
            this.listenTo(this.model, 'change:body', this.render);
            this.render();
        },
        render: function() {
            var source = this.model.get('body');
            var html = typeset_body(source, function(text, tag) {
                return '<a href="#" rel="tooltip" data-original-title="tag: ' + tag + '"><i>' + text + '</i></a>';
            }, function(text, item_id) {
                return '<a href="#" rel="tooltip" data-original-title="item: ' + item_id + '"><b>' + text + '</b></a>';
            });
            this.$el.html(html);
            this.$el.tooltip({ selector: "a[rel=tooltip]" });
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, this.$el.get()]);
        }
    });

    var SaveDraftView = Backbone.View.extend({
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
                    redirect(to_url.drafts_show(model.get('id')));
                },
                error: function(model, error) {
                    console.log(model.toJSON());
                    console.log('error saving');
                }
            });
        }
    });

    var AddCategoryView = Backbone.View.extend({
        events: {
            'click #category-minus-btn': 'minusAction',
            'click #category-plus-btn':  'plusAction',
            'keypress input':            'keyPress'
        },
        initialize: function() {
            _.bindAll(this, 'render', 'renderTags', 'keyPress', 'addAction', 'minusAction', 'plusAction', 'modalReady');
            this.collection = new TagList();
            this.listenTo(this.collection, 'add remove', this.renderTags);
            this.render();
        },
        render: function() {
            this.$el.html(Handlebars.templates.add_category());
            this.input_element = this.$('input');
            return this;
        },
        modalReady: function(dispatcher) {
            this.listenTo(dispatcher, 'add', this.addAction);
            this.dispatcher = dispatcher;
            this.input_element.focus();
        },
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
            if (e.which == 13) {
                if (this.input_element.val()) {
                    this.plusAction();
                } else if (this.collection.length) {
                    this.addAction();
                }
            }
        },
        addAction: function() {
            this.options.add(new Category({
                tag_list: this.collection
            }));
            this.dispatcher.trigger('close');
        },
        minusAction: function() {
            if (!this.input_element.val())
                this.collection.pop();
            this.input_element.val('').focus();
        },
        plusAction: function() {
            var value = trim(this.input_element.val());
            if (value)
                this.collection.push({ name: value });
            this.input_element.val('').focus();
        }
    });

    function show_add_category_modal(callback) {
        show_modal('Add category',
                   new AddCategoryView({ add: callback }),
                   [{ name: 'Add category', signal: 'add', primary: true },
                    { name: 'Cancel', signal: 'close' }]);
    }

    var RemovableCategoryView = Backbone.View.extend({
        tagName: 'span',
        className: 'category',
        events: {
            'click .delete-category': function() {
                this.model.destroy();
            }
        },
        initialize: function() {
            _.bindAll(this, 'render');
            this.listenTo(this.model, 'change', this.render);
            this.listenTo(this.model, 'remove', this.remove);
        },
        render: function() {
            var tag_html = this.model.typeset();
            this.$el.html(tag_html + ' <a href="#" class="glyphicon glyphicon-remove delete-category"></a>');
            return this;
        }
    });

    var EditableCategoryListView = Backbone.View.extend({
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
            var collection = this.collection;
            show_add_category_modal(function(category) {
                collection.add(category);
            });
        }
    });

    var ChangableTagAssociationView = Backbone.View.extend({
        // standard
        tagName: 'tr',
        events: {
            'click button': '_change'
        },
        initialize: function() {
            _.bindAll(this, 'render', '_change');
            this.listenTo(this.model, 'change', this.render);
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
            var model = this.model;
            show_add_category_modal(function(category) {
                model.set('category', category);
            });
        }
    });

    var ChangableTagAssociationListView = Backbone.View.extend({
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
            var tagAssociation = new ChangableTagAssociationView({
                model: item
            });
            this.$('tbody').append(tagAssociation.render().el);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, tagAssociation.$el.get()]);
        }
    });

    var SaveFinalView = Backbone.View.extend({
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
                    redirect(to_url.items_show_final(model.get('id')));
                },
                error: function(model, error) {
                    console.log(model.toJSON());
                    console.log('error saving');
                }
            });
        }
    });

    var sourceFields = {
        'author':    { 'type': 'array',  'size': '4', 'maxlen': 255, 'name': 'Author' },
        'editor':    { 'type': 'array',  'size': '4', 'maxlen': 255, 'name': 'Editor' },
        'title':     { 'type': 'string', 'size': '8', 'maxlen': 255, 'name': 'Title' },
        'publisher': { 'type': 'string', 'size': '4', 'maxlen': 255, 'name': 'Publisher' },
        'year':      { 'type': 'string', 'size': '2', 'maxlen': 32,  'name': 'Year' },
        'volume':    { 'type': 'string', 'size': '2', 'maxlen': 255, 'name': 'Volume' },
        'number':    { 'type': 'string', 'size': '2', 'maxlen': 255, 'name': 'Number' },
        'series':    { 'type': 'string', 'size': '4', 'maxlen': 255, 'name': 'Series' },
        'address':   { 'type': 'string', 'size': '4', 'maxlen': 255, 'name': 'Address' },
        'edition':   { 'type': 'string', 'size': '2', 'maxlen': 255, 'name': 'Edition' },
        'month':     { 'type': 'string', 'size': '2', 'maxlen': 255, 'name': 'Month' },
        'journal':   { 'type': 'string', 'size': '4', 'maxlen': 255, 'name': 'Journal' },
        'pages':     { 'type': 'string', 'size': '2', 'maxlen': 255, 'name': 'Pages' },
        'isbn10':    { 'type': 'string', 'size': '4', 'maxlen': 32,  'name': '10-digit ISBN' },
        'isbn13':    { 'type': 'string', 'size': '4', 'maxlen': 32,  'name': '13-digit ISBN' },
        'note':      { 'type': 'string', 'size': '8', 'maxlen': 255, 'name': 'Note' }
    };

    var sourceTypes = {
        'book': {
            'name': 'Book',
            'show': ['author', 'title', 'publisher', 'year'],
            'extra': ['isbn10', 'isbn13', 'editor', 'volume', 'number', 'series', 'address', 'edition', 'month', 'note']
        },
        'article': {
            'name': 'Article',
            'show': ['author', 'title', 'journal', 'year'],
            'extra': ['volume', 'number', 'pages', 'month', 'note']
        }
    };

    var SourceEditView = Backbone.View.extend({
        events: {
            'change #select-source': function() {
                this._setType(this.$('#select-source').val());
            },
            'click #extra-fields a': function(event) {
                this._addExtra($(event.currentTarget).data('key'));
            },
            'click #source-fields a': function(event) {
                var field_key = $(event.currentTarget).data('key');
                var value = this.model.has(field_key) ? this.model.get(field_key): [''];
                this.model.set(field_key, value.concat(''));
                this.render();
            },
            'click #add-source': function() {
                var self = this;
                this.model.save(null, {
                    wait: true,
                    success: function(model, response) {
                        if (self.options.mode[0] == 'item') {
                            redirect(to_url.sources_add_location_for_item(self.options.mode[1], model.get('id')));
                        } else if (self.options.mode[0] == 'draft') {
                            redirect(to_url.sources_add_location_for_draft(self.options.mode[1], model.get('id')));
                        } else {
                            redirect(to_url.source_index());
                        }
                    },
                    error: function(model, error) {
                        console.log(model.toJSON());
                        console.log('error saving source');
                    }
                });
            }
        },
        initialize: function() {
            _.bindAll(this, 'render', '_setType', '_updateModel', '_addExtra');
            this.listenTo(this.$el, 'input propertychange', this._updateModel);
            this._setType(this.model.get('type'));
        },
        _setType: function(type) {
            var attrs = cleanValues(this.model.attributes);
            attrs.type = type;
            this.model.clear({
                'silent': true
            });
            this.model.set(attrs);
            this.render();
        },
        _addExtra: function(name) {
            var v = sourceFields[name].type == 'array' ? [''] : '';
            this.model.set(name, v);
            this.render();
        },
        render: function() {
            var type = this.model.get('type');

            var type_data = sourceTypes[type];
            var extras_to_show = _.filter(type_data.extra, function(element) {
                return this.model.has(element);
            }, this);

            var html = Handlebars.templates.source_edit({
                'types': _.map(sourceTypes, function(value, key) {
                    return {
                        'key': key,
                        'name': sourceTypes[key].name
                    };
                }),
                'extra': _.map(_.difference(type_data.extra, extras_to_show), function(key) {
                    return {
                        'key': key,
                        'name': sourceFields[key].name
                    };
                })
            });
            this.$el.html(html);

            this.$('#select-source').val(type);

            var source_fields_element = this.$('#source-fields');
            var show = _.union(type_data.show, extras_to_show);

            _.each(show, function(field_key) {
                var field_config = sourceFields[field_key];
                var data = {
                    'id': field_key,
                    'name': field_config.name,
                    'size': field_config.size,
                    'max': field_config.maxlen,
                    'value': this.model.has(field_key) ? this.model.get(field_key): (field_config.type == 'array' ? [''] : '')
                };
                if (field_config.type == 'string') {
                    source_fields_element.append(Handlebars.templates.source_string_field(data));
                } else if (field_config.type == 'array') {
                    source_fields_element.append(Handlebars.templates.source_array_field(data));
                }
            }, this);

            this.delegateEvents();

            this.$('input[type="text"]').first().focus();
        },
        _updateModel: function() {
            var view = this, key, value;
            view.$('input').each(function() {
                key = $(this).attr('id').slice(6);
                if (key.match(/^[a-z]+$/) || key.match(/^isbn(10|13)$/)) {
                    value = $(this).val();
                    value ? view.model.set(key, value) : view.model.unset(key);
                } else if (key.match(/^[a-z]+0$/)) {
                    key = key.slice(0, -1);
                    var idBase = '#input-' + key;
                    value = [];
                    for (var j = 0; ; j++) {
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

    var SourceRenderView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');
            this.listenTo(this.model, 'change', this.render);
            this.render();
        },
        render: function() {
            this.$el.html(typeset_source(this.model.attributes));
        }
    });

    var SourceSearchItemView = Backbone.View.extend({
        tagName: 'a',
        className: 'list-group-item',
        attributes: function() {
            var url = '#';
            if (this.options.mode[0] == 'item') {
                url = to_url.sources_add_location_for_item(this.options.mode[1], this.model.get('id'));
            } else if (this.options.mode[0] == 'draft') {
                url = to_url.sources_add_location_for_draft(this.options.mode[1], this.model.get('id'));
            }
            return {
                'href': url
            };
        },
        initialize: function() {
            _.bindAll(this, 'render');
            this.render();
        },
        render: function() {
            this.$el.html(Handlebars.templates.source_search_item({
                'source': typeset_source(this.model.attributes)
            }));
            return this;
        }
    });

    var LiveSourceSearchView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render', '_search', '_check', '_cancelTimer', '_addOne');
            this.listenTo(this.options.sourceModel, 'change', this._check);
            this.collection = new Backbone.Collection;
            this.collection.url = api_prefix + 'source/search';
            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this._addOne);
            this.render();
            this._search();
        },
        render: function() {
            this.$el.html(Handlebars.templates.source_search_container());
            this.collection.each(this._addOne);
        },
        _addOne: function(item) {
            var itemView = new SourceSearchItemView({
                model: item,
                mode: this.options.mode
            });
            this.$('.no-matches-message').hide();
            this.$('div').append(itemView.render().el);
        },
        _search: function() {
            this._cancelTimer();
            var attrs = cleanValues(this.options.sourceModel.attributes);
            for (var key in attrs) {
                if (_.isArray(attrs[key])) {
                    attrs[key] = JSON.stringify(attrs[key]);
                }
            }
            if (_.isEmpty(_.pick(attrs, 'author', 'title', 'isbn10', 'isbn13'))) {
                this.collection.reset();
            } else {
                this.collection.fetch({
                    'data': attrs,
                    'reset': true
                });
            }
        },
        _check: function() {
            this._cancelTimer();
            this.timeoutID = window.setTimeout(this._search, 1000);
        },
        _cancelTimer: function() {
            if (typeof this.timeoutID == "number") {
                window.clearTimeout(this.timeoutID);
                delete this.timeoutID;
            }
        }
    });

    var ValidationView = Backbone.View.extend({
        tagName: 'li',
        className: 'list-group-item',
        initialize: function() {
            _.bindAll(this, 'render');
            this.render();
        },
        render: function() {
            this.$el.html(Handlebars.templates.validation_item({
                'source': typeset_source(this.model.get('source')),
                'location': this.model.get('location')
            }));
            return this;
        }
    });

    var ValidationListView = Backbone.View.extend({
        // standard
        initialize: function() {
            _.bindAll(this, 'render', '_addOne');
            this.collection.bind('add', this._addOne);
            this.render();
        },
        render: function() {
            this.$el.html(Handlebars.templates.validation_list());
            this.collection.each(this._addOne);
        },
        // helpers
        _addOne: function(item) {
            var validationView = new ValidationView({
                model: item
            });
            this.$('ul').append(validationView.render().el);
        }
    });

    var SourceListView = Backbone.View.extend({
        // standard
        initialize: function() {
            _.bindAll(this, 'render', '_addOne');
            this.collection.bind('reset', this.render);
            this.render();
        },
        render: function() {
            this.$el.html(Handlebars.templates.source_list_container());
            this.collection.each(this._addOne);
        },
        // helpers
        _addOne: function(item) {
            var html = Handlebars.templates.source_list_item({
                'link': '#', //to_url.source_item(item.get('id')),
                'source': typeset_source(item.attributes)
            });
            this.$('div').append(html);
        }
    });

    var DocumentMessageView = Backbone.View.extend({
        id: function() {
            return 'doc-entry-' + this.model.cid;
        },
        className: function() {
            return 'alert alert-dismissable alert-' + this.model.get('severity');
        },
        events: {
            'click .close': 'remove'
        },
        initialize: function() {
            _.bindAll(this, 'render');
        },
        render: function() {
            this.$el.html(Handlebars.templates.document_message({
               message: this.model.get('message')
            }));
            return this;
        }
    });

    var DocumentItemView = Backbone.View.extend({
        className: 'panel panel-default',
        events: {
            'click a.add-concept': function(e) {
                e.preventDefault();
                var elem = $(e.currentTarget);
                this.options.dispatcher.trigger('add-concept', elem.data('concept'), this.id.slice(10));
            },
            'click a.add-item': function(e) {
                e.preventDefault();
                var elem = $(e.currentTarget);
                this.options.dispatcher.trigger('add-item', elem.data('item'), this.id.slice(10));
            },
            'click .close': function() {
                this.options.dispatcher.trigger('remove', this.model.get('id'));
            }
        },
        initialize: function() {
            _.bindAll(this, 'render');
        },
        render: function() {
            var tag_refs = this.model.get('tag_refs');
            var body = typeset_body(this.model.get('body'), function(text, tag) {
                var concept_id = tag_refs[tag];
                return '<a href="#" class="add-concept concept-' + concept_id + '-ref" data-concept="'
                        + concept_id + '">' + text + '</a>';
            }, function(text, item_id) {
                return '<a href="#" class="add-item item-' + item_id + '-ref" data-item="' + item_id + '">' + text + '</a>';
            });
            var html = Handlebars.templates.document_item({
                title: this.model.get('name'),
                link:  this.model.get('link'),
                body:  body
            });
            this.$el.html(html);
            return this;
        }
    });

    var DocumentView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render', 'onAdd', 'makeItemView', 'fetchConcept', 'fetchItem', 'fetch',
                            'removeEntryView', 'updateReferenceAvailability');
            this.listenTo(this.collection, {
                'reset': this.render,
                'add':   this.onAdd
            });
            this.dispatcher = _.clone(Backbone.Events);
            this.listenTo(this.dispatcher, {
                'add-item':    this.fetchItem,
                'add-concept': this.fetchConcept,
                'remove':      this.removeEntryView
            });
            this.concepts_unavailable = {};
            this.render();
        },
        render: function() {
            this.$el.empty();
            this.collection.each(function(model) {
                var view = this.makeItemView(model);
                model.set('view', view);
                this.$el.append(view.render().el);
            }, this);
            this.updateReferenceAvailability();
        },
        insertItemView: function(model, view) {
            this.collection.remove(model);
            var pos = 0, model_order = model.get('order');
            while (pos < this.collection.length && model_order > this.collection.at(pos).get('order'))
                pos++;
            view.render();
            if (pos < this.collection.length) {
                var pos_model = this.collection.at(pos);
                $('#doc-entry-' + (pos_model.id || pos_model.cid)).before(view.el);
            } else
                this.$el.append(view.el);
            model.set('view', view);
            this.collection.add(model, { at: pos, silent: true });
        },
        onAdd: function(model) {
            var msgView;
            switch (model.get('type')) {
                case 'item':
                    var itemView = this.makeItemView(model);
                    this.insertItemView(model, itemView);
                    MathJax.Hub.Queue(["Typeset", MathJax.Hub, itemView.$el.get()]);
                    if (model.has('for_concept')) {
                        var concept_html = typeset_category_id(model.get('for_concept'));
                        model.unset('for_concept');
                        msgView = this.makeMessageView('success', model.get('name') + ' defining ' + concept_html + ' was inserted');
                    } else {
                        msgView = this.makeMessageView('success', model.get('name') + ' was inserted');
                    }
                    itemView.$el.before(msgView.render().el);
                    break;
                case 'concept-not-found':
                    this.collection.remove(model);
                    var concept_id = model.get('concept');
                    var concept_html = typeset_category_id(concept_id);
                    msgView = this.makeMessageView('warning', 'Definition for ' + concept_html + ' not found');
                    this.concepts_unavailable['' + concept_id] = false;
                    $('#doc-entry-' + model.get('source_id')).before(msgView.render().el);
                    break;
                case 'item-removed':
                    var target_model = this.collection.get(model.get('entry_id'));
                    var target_view = target_model.get('view');
                    msgView = this.makeMessageView('success', model.get('name') + ' was removed');
                    target_view.$el.before(msgView.render().el);
                    this.collection.remove(model);
                    this.collection.remove(target_model);
                    target_view.remove();
                    break;
            }
            this.updateReferenceAvailability();
            scrollTo(msgView.$el);
        },
        updateReferenceAvailability: function() {
            this.item_availability = {};
            this.concept_availability = _.clone(this.concepts_unavailable);
            this.collection.each(function(model) {
                _.each(model.get('item_defs'), function(item_id) {
                    this.item_availability[item_id] = model.get('id');
                }, this);
                _.each(model.get('concept_defs'), function(concept_id) {
                    this.concept_availability['' + concept_id] = model.get('id');
                }, this);
            }, this);
            this.$('a.add-item').removeClass('text-success');
            _.each(this.item_availability, function(value, key) {
                this.$('a.item-' + key + '-ref').addClass('text-success');
            }, this);
            this.$('a.add-concept').removeClass('text-success text-warning');
            _.each(this.concept_availability, function(value, key) {
                var has_concept = typeof value === 'string';
                this.$('a.concept-' + key + '-ref').addClass(has_concept ? 'text-success' : 'text-warning');
            }, this);
        },
        makeItemView: function(model) {
            return new DocumentItemView({
                id: 'doc-entry-' + model.id,
                model: model,
                dispatcher: this.dispatcher
            });
        },
        makeMessageView: function(severity, message) {
            return new DocumentMessageView({
                model: new Backbone.Model({
                    severity: severity,
                    message: message
                })
            });
        },
        fetch: function(subpath, data) {
            this.$('.alert').remove();
            this.collection.fetch({
                url: this.collection.url + this.options.doc_id + '/' + subpath,
                type: 'POST',
                data: JSON.stringify(data),
                remove: false
            });
        },
        fetchConcept: function(concept_id, source_id) {
            var key = '' + concept_id;
            if (this.concept_availability[key]) {
                scrollTo($('#doc-entry-' + this.concept_availability[key]));
            } else {
                this.fetch('add-concept', {
                    concept: concept_map.from_id(concept_id),
                    source_id: source_id
                });
            }
        },
        fetchItem: function(item_id, source_id) {
            if (this.item_availability[item_id]) {
                scrollTo($('#doc-entry-' + this.item_availability[item_id]));
            } else {
                this.fetch('add-item', {
                    item_id: item_id
                });
            }
        },
        removeEntryView: function(item_id) {
            this.fetch('delete', item_id);
        }
    });

    var DocumentRenameView = Backbone.View.extend({
        events: {
            'keypress input': 'keyPress'
        },
        initialize: function() {
            _.bindAll(this, 'render', 'modalReady', 'keyPress', 'save');
            this.render();
        },
        render: function() {
            this.$el.html('<input type="text" class="form-control" placeholder="document name" max-length="255">');
            return this;
        },
        modalReady: function(dispatcher) {
            this.dispatcher = dispatcher;
            this.listenTo(dispatcher, 'save', this.save);
        },
        keyPress: function(e) {
            if (e.which == 13) this.save();
        },
        save: function() {
            this.model.save({ title: this.$('input').val() }, { wait: true });
            this.dispatcher.trigger('close');
        }
    });

    /****************************
     * Pages
     ****************************/

    var teoremer = {
        home: function(init_items) {
            new TopListView({
                el: $('#top-item-list'),
                collection: new TopList(init_items, { parse: true })
            });
        },

        source_list: function(items) {
            new SourceListView({
                el: $('#source-list'),
                collection: new SourceList(items)
            });
        },

        new_draft: function(kind, show_primcats, parent) {
            var draft_data = { type: kind };
            if (parent) draft_data.parent = parent;
            var item = new DraftItem(draft_data, { parse: true });

            new BodyEditView({
                el: $('#body-input'),
                model: item
            });
            new BodyPreviewView({
                el: $('#body-preview'),
                model: item
            });
            new SaveDraftView({
                el: $('#save-draft'),
                model: item
            });
            if (show_primcats) {
                new EditableCategoryListView({
                    el: $('#primary-categories'),
                    collection: item.get('pricats')
                });
            }
            new EditableCategoryListView({
                el: $('#secondary-categories'),
                collection: item.get('seccats')
            });
        },

        edit_draft: function(id, body, pricats, seccats, show_primcats) {
            var item = new DraftItem({ id: id, body: body, pricats: pricats, seccats: seccats }, { parse: true });
            new BodyEditView({
                el: $('#body-input'),
                model: item
            });
            new BodyPreviewView({
                el: $('#body-preview'),
                model: item
            });
            new SaveDraftView({
                el: $('#save-draft'),
                model: item
            });
            if (show_primcats) {
                new EditableCategoryListView({
                    el: $('#primary-categories'),
                    collection: item.get('pricats')
                });
            }
            new EditableCategoryListView({
                el: $('#secondary-categories'),
                collection: item.get('seccats')
            });
        },

        show_draft: function(validations) {
            $(function() {
                $('div.draft-view').tooltip({
                  selector: "a[rel=tooltip]"
                });
            });
            new ValidationListView({
                el: $('#validation-list'),
                collection: new ValidationList(validations)
            });
        },

        edit_final: function(id, pricats, seccats, tagcatmap, show_primcats) {
            var item = new FinalItem({
                id: id,
                pricats: pricats,
                seccats: seccats,
                tagcatmap: tagcatmap
            }, { parse: true });

            new SaveFinalView({
                el: $('#save'),
                model: item
            });
            if (show_primcats) {
                new EditableCategoryListView({
                    el: $('#primary-categories'),
                    collection: item.get('pricats')
                });
            }
            new EditableCategoryListView({
              el: $('#secondary-categories'),
              collection: item.get('seccats')
            });
            new ChangableTagAssociationListView({
              el: $('#tag-to-category-map'),
              collection: item.get('tagcatmap')
            });
        },

        item_search: function(itemtypes, statuses, init_items, category, restrict, user_id) {
            var includeView = new TagListView({
                el: $('#include-tags')
            });
            var excludeView = new TagListView({
                el: $('#exclude-tags')
            });
            var searchTerms = new SearchTerms();
            if (typeof category != 'undefined')
                searchTerms.set('category', category);
            var searchListViewData = {
                el: $('#search-item-list'),
                collection: new SearchList(init_items, { parse: true }),
                itemtypes: itemtypes,
                statuses: statuses,
                parameters: searchTerms
            };
            if (restrict) {
                searchListViewData.restrict = {
                    user: user_id,
                    statuses: restrict
                };
            }
            new SearchListView(searchListViewData);

            includeView.collection.on('add remove', function() {
              searchTerms.set('includeTags', includeView.getTagList());
            });
            excludeView.collection.on('add remove', function() {
              searchTerms.set('excludeTags', excludeView.getTagList());
            });
        },

        show_final: function(validations, parent, user_id, init_proofs) {
            new ValidationListView({
                el: $('#validation-list'),
                collection: new ValidationList(validations)
            });

            if (parent) {
                var searchTerms = new SearchTerms({
                    parent: parent
                });
                var searchListViewData = {
                    el: $('#proof-list'),
                    collection: new SearchList(init_proofs, { parse: true }),
                    itemtypes: 'P',
                    parameters: searchTerms
                };
                if (user_id) {
                    searchListViewData.statuses = 'FRD';
                    searchListViewData.restrict = {
                        user: user_id,
                        statuses: 'D'
                    };
                } else {
                    searchListViewData.statuses = 'FR';
                }
                var searchList = new SearchListView(searchListViewData);
            }
        },

        source_add: function(mode) {
            var source = new SourceItem();
            new SourceEditView({ el: $('#source-edit'), model: source, mode: mode });
            new SourceRenderView({ el: $('#source-preview'), model: source });
            new LiveSourceSearchView({ el: $('#source-search'), sourceModel: source, mode: mode });
        },

        source_preview: function(source) {
            new SourceRenderView({
                el: $('#source-preview'),
                model: new SourceItem(source)
            });
        },

        document_view: function(data, items) {
            var document_data = new DocumentModel(data);
            var set_title = function() {
                $('#document-title').html('Document ' + (document_data.escape('title') || data.id));
            };
            set_title();
            document_data.on('change:title', set_title);
            new DocumentView({
                el: $('#document-items'),
                doc_id: data.id,
                collection: new DocumentItemList(items, { parse: true })
            });
            $('#rename-button').click(function() {
                show_modal('Rename document',
                           new DocumentRenameView({ model: document_data }),
                           [ { name: 'Close' }, { name: 'Save', primary: true } ]);
            });
        }
    };

    window.teoremer = teoremer;

})();

// on load actions

$(function() {

    function expanderToggle(elem) {
        elem.toggleClass('expander-in').toggleClass('expander-out');
        elem.find('span.glyphicon').toggleClass('glyphicon-chevron-down').toggleClass('glyphicon-chevron-up');
        elem.next().toggle();
    }

    $('.expander-in').each(function() {
        $(this).next().hide();
        $(this).find('span.glyphicon').addClass('glyphicon-chevron-down');
    }).click(function() {
        expanderToggle($(this));
    });

    $('expander-out').each(function() {
        $(this).find('span.glyphicon').addClass('glyphicon-chevron-up');
        $(this).next().show();
    }).click(function() {
        expanderToggle($(this));
    });

    $(function() {
        $('input.focus').first().focus();
    });

});
