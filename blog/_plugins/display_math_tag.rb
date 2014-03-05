module Jekyll
  class DisplayMathTag < Liquid::Tag

    def initialize(tag_name, source, tokens)
      super
      @source = source
    end

    def render(context)
      "\\\\\[#{@source}\\\\\]"
    end
  end
end

Liquid::Template.register_tag('display_math', Jekyll::DisplayMathTag)

