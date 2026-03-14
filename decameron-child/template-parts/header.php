<?php
/**
 * Template Part: Site Header
 * Injected on every page via the wp_body_open hook in functions.php.
 */
?>

<header class="site-header" role="banner">
    <nav class="dec-top-nav" role="navigation" aria-label="Main navigation">
        <?php
        wp_nav_menu( array(
            'theme_location' => 'primary-menu',
            'container'      => false,
            'menu_class'     => 'main-menu',
            'fallback_cb'    => function() {
                echo '<ul class="main-menu">';
                echo '<li><a href="' . esc_url( home_url() ) . '">Home</a></li>';
                echo '<li><a href="' . esc_url( home_url('/proemio-prologue/') ) . '">Read</a></li>';
                echo '</ul>';
            },
        ) );
        ?>
    </nav>
</header>
