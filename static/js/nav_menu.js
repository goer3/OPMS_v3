+function ($) {
    $(function () {

        var num_test = 1
        // class
        $(document).on('click', '[data-toggle^="class"]', function (e) {
            e && e.preventDefault();

            console.log('abc');

            if (num_test % 2 == 0) {
                $('#aside-user').show();
                $('#coll_tag_doc').show();
                $('#coll_tag_ops').show();
                $('#coll_tag_plat').show();
            } else {
                $('#aside-user').hide();
                $('#coll_tag_doc').hide();
                $('#coll_tag_ops').hide();
                $('#coll_tag_plat').hide();
            }


            num_test++

            var $this = $(e.target), $class, $target, $tmp, $classes, $targets;
            !$this.data('toggle') && ($this = $this.closest('[data-toggle^="class"]'));
            $class = $this.data()['toggle'];
            $target = $this.data('target') || $this.attr('href');
            $class && ($tmp = $class.split(':')[1]) && ($classes = $tmp.split(','));
            $target && ($targets = $target.split(','))
            $classes && $classes.length && $.each($targets, function (index, value) {
                if ($classes[index].indexOf('*') !== -1) {
                    var patt = new RegExp('\\s' +
                        $classes[index].replace(/\*/g, '[A-Za-z0-9-_]+').split(' ').join('\\s|\\s') +
                        '\\s', 'g');
                    $($this).each(function (i, it) {
                        var cn = ' ' + it.className + ' ';
                        while (patt.test(cn)) {
                            cn = cn.replace(patt, ' ');
                        }
                        it.className = $.trim(cn);
                    });
                }
                ($targets[index] != '#') && $($targets[index]).toggleClass($classes[index]) || $this.toggleClass($classes[index]);
            });
            $this.toggleClass('active');
        });

        // collapse nav
        $(document).on('click', 'nav a', function (e) {
            var $this = $(e.target), $active;
            $this.is('a') || ($this = $this.closest('a'));

            $active = $this.parent().siblings(".active");
            $active && $active.toggleClass('active').find('> ul:visible').slideUp(200);

            ($this.parent().hasClass('active') && $this.next().slideUp(200)) || $this.next().slideDown(200);
            $this.parent().toggleClass('active');

            $this.next().is('ul') && e.preventDefault();

            setTimeout(function () {
                $(document).trigger('updateNav');
            }, 300);
        });
    });
}(jQuery);
