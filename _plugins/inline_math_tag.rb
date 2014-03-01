module Jekyll
  class InlineMathTag < Liquid::Tag

    def initialize(tag_name, source, tokens)
      super
      @source = source
    end

    def render(context)
      "foo #{@source} bar"
    end
  end
end

Liquid::Template.register_tag('inline_math', Jekyll::InlineMathTag)

