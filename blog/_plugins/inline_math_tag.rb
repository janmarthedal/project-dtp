module Jekyll
  class InlineMathTag < Liquid::Tag

    def initialize(tag_name, source, tokens)
      super
      @source = source
    end

    def render(context)
      #t = @source.gsub(/([\\{}\[\]*_+.!-])/, '\\ \1')
      #print t
      #"\\\\\(#{@source}\\\\\)"
      "foobar"
    end
  end
end

Liquid::Template.register_tag('inline_math', Jekyll::InlineMathTag)

