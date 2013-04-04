(function(window){

    var $ = window.jQuery;

    var teoremer = {}

    function typeset_tag(st) {
      var elems = st.split('$');
      for (var n=0; n < elems.length; n++) {
          if (n % 2 != 0) {
              elems[n] = '\\(' + elems[n] + '\\)';
          }
      }
      return elems.join('');
    }

    teoremer.TagItem = Backbone.Model.extend({
    });
  
    teoremer.TagList = Backbone.Collection.extend({
        model: teoremer.TagItem
    });

    teoremer.TagItemView = Backbone.View.extend({
        tagName: 'span',
        className: 'tag',
        events: { 
            'click .delete-tag': 'remove'
        },    
        initialize: function() {
            _.bindAll(this, 'render', 'unrender', 'remove');
            this.model.bind('change', this.render);
            this.model.bind('remove', this.unrender);
        },
        render: function() {
            var tag_html = typeset_tag(this.model.get('name'));
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
        events: {},
        initialize: function() {
            _.bindAll(this, 'render', 'addItem', 'appendItem', 'keyPress');
            this.collection = new teoremer.TagList();
            this.collection.bind('add', this.appendItem);
            this.events['click #' + this.options.prefix + '-tag-add'] = 'addItem';
            this.events['keypress #' + this.options.prefix + '-tag-name'] = 'keyPress';
            this.render();
            this.input_field = $('#' + this.options.prefix + '-tag-name');
            this.input_field.typeahead({
                source:
                    function(query, process) {
                        $.get('/api/tags/prefixed/' + query, function(data) { process(data); }, 'json');
                    }
            });
        },
        render: function() {
            var self = this;
            var html = Handlebars.templates.tag_list_input({ prefix: this.options.prefix });
            this.$el.html(html);
            _(this.collection.models).each(function(item){
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
            $('#' + this.options.prefix + '-tag-list').append(tagItemView.render().el);
        }
    });

    window.teoremer = teoremer;

})(window);
