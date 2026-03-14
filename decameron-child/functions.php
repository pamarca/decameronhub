<?php
/**
 * Decameron Child Theme v4 - ULTRA FIX
 * Manually filter to avoid get_pages meta_query bugs
 */

// Enqueue styles and scripts
add_action( 'wp_enqueue_scripts', 'decameron_enqueue', 20 );
function decameron_enqueue() {
    wp_enqueue_style(
        'twentytwentyfive-style',
        get_template_directory_uri() . '/style.css'
    );

    wp_enqueue_style(
        'decameron-child-style',
        get_stylesheet_directory_uri() . '/style.css',
        array( 'twentytwentyfive-style' ),
        '4.0'
    );

    // mobile-nav.js: top-nav hamburger + sidebar toggle — needed on every page
    wp_enqueue_script(
        'decameron-mobile-nav',
        get_stylesheet_directory_uri() . '/js/mobile-nav.js',
        array(),
        '4.0',
        true
    );

    // Full reading JS only on Decameron content pages
    if ( is_page() && get_post_meta( get_the_ID(), '_decameron_type', true ) ) {
        wp_enqueue_script(
            'decameron-js',
            get_stylesheet_directory_uri() . '/js/decameron.js',
            array(),
            '4.0',
            true
        );
        wp_localize_script( 'decameron-js', 'decamerOnData', decameron_nav_data() );
    }
}

// Register navigation menu
register_nav_menus( array(
    'primary-menu' => __( 'Primary Menu', 'decameron-child' ),
) );

// Build nav data — currentId is page-specific, so only the nav list is cached.
function decameron_nav_data() {
    return array(
        'nav'       => decameron_build_nav(),
        'currentId' => get_the_ID(),
    );
}

// Build and cache the sidebar nav structure (one DB query, cached for a day).
function decameron_build_nav() {
    $cached = get_transient( 'decameron_nav' );
    if ( $cached !== false ) {
        return $cached;
    }

    // Single query for all Decameron pages.
    $all_pages = get_pages( array( 'number' => 1000 ) );

    // Read all relevant meta in one pass.
    $by_type = array();  // type => [pages]
    $by_day  = array();  // day_number => [pages]

    foreach ( $all_pages as $page ) {
        $type  = get_post_meta( $page->ID, '_decameron_type', true );
        $day   = (int) get_post_meta( $page->ID, '_decameron_day',   true );
        $order = (int) get_post_meta( $page->ID, '_decameron_order', true );

        if ( ! $type ) continue;

        // Attach meta to the page object so we don't re-query later.
        $page->_dec_type  = $type;
        $page->_dec_day   = $day;
        $page->_dec_order = $order;

        $by_type[ $type ][] = $page;
        if ( $day > 0 ) {
            $by_day[ $day ][] = $page;
        }
    }

    $days = array();

    // Prologue
    if ( ! empty( $by_type['prologue'] ) ) {
        $p = $by_type['prologue'][0];
        $days[] = array(
            'type'  => 'single',
            'label' => 'Proemio / Prologue',
            'url'   => get_permalink( $p->ID ),
            'id'    => $p->ID,
        );
    }

    // Days 1–10
    for ( $d = 1; $d <= 10; $d++ ) {
        if ( empty( $by_day[ $d ] ) ) continue;

        $day_pages = $by_day[ $d ];

        // Sort by _decameron_order.
        usort( $day_pages, function( $a, $b ) {
            return $a->_dec_order - $b->_dec_order;
        });

        // Find day_intro (order = 0).
        $day_intro = null;
        foreach ( $day_pages as $page ) {
            if ( $page->_dec_type === 'day_intro' && $page->_dec_order === 0 ) {
                $day_intro = $page;
                break;
            }
        }

        $children = array();
        foreach ( $day_pages as $page ) {
            $type  = $page->_dec_type;
            $order = $page->_dec_order;

            if ( $type === 'day_intro' ) continue;

            if ( $type === 'introduction' ) {
                $children[] = array(
                    'label' => 'Introduzione / Introduction',
                    'url'   => get_permalink( $page->ID ),
                    'id'    => $page->ID,
                );
            } elseif ( $type === 'novella' ) {
                $novella_num = $order - 1; // order 2–11 → novella 1–10
                $children[] = array(
                    'label' => 'Novella ' . $novella_num,
                    'url'   => get_permalink( $page->ID ),
                    'id'    => $page->ID,
                );
            } elseif ( $type === 'conclusion' ) {
                $children[] = array(
                    'label' => 'Conclusione / Conclusion',
                    'url'   => get_permalink( $page->ID ),
                    'id'    => $page->ID,
                );
            }
        }

        $days[] = array(
            'type'     => 'day',
            'label'    => 'Giornata ' . $d . ' / Day ' . $d,
            'url'      => $day_intro ? get_permalink( $day_intro->ID ) : '#',
            'id'       => $day_intro ? $day_intro->ID : 0,
            'day'      => $d,
            'children' => $children,
        );
    }

    // Epilogue
    if ( ! empty( $by_type['epilogue'] ) ) {
        $e = $by_type['epilogue'][0];
        $days[] = array(
            'type'  => 'single',
            'label' => 'Epilogo / Epilogue',
            'url'   => get_permalink( $e->ID ),
            'id'    => $e->ID,
        );
    }

    set_transient( 'decameron_nav', $days, DAY_IN_SECONDS );
    return $days;
}

// Bust nav caches whenever any page is saved.
add_action( 'save_post', function() {
    delete_transient( 'decameron_nav' );
    delete_transient( 'decameron_ordered_pages' );
});

// Return prev/next pages in reading order for the given page ID.
function decameron_adjacent_pages( $current_id ) {
    $ordered = get_transient( 'decameron_ordered_pages' );

    if ( $ordered === false ) {
        $all_pages = get_pages( array( 'number' => 1000 ) );
        $dec_pages = array();

        foreach ( $all_pages as $page ) {
            $type  = get_post_meta( $page->ID, '_decameron_type',  true );
            if ( ! $type ) continue;
            $day   = (int) get_post_meta( $page->ID, '_decameron_day',   true );
            $order = (int) get_post_meta( $page->ID, '_decameron_order', true );

            // Global sort: prologue=0, days 1–10 scaled by 100, epilogue=1100
            if ( $type === 'prologue' )     $sort_day = 0;
            elseif ( $type === 'epilogue' ) $sort_day = 11;
            else                            $sort_day = $day;

            $dec_pages[] = array(
                'id'       => $page->ID,
                'title'    => get_the_title( $page->ID ),
                'url'      => get_permalink( $page->ID ),
                'sort_key' => $sort_day * 100 + $order,
            );
        }

        usort( $dec_pages, function( $a, $b ) {
            return $a['sort_key'] - $b['sort_key'];
        });

        set_transient( 'decameron_ordered_pages', $dec_pages, DAY_IN_SECONDS );
        $ordered = $dec_pages;
    }

    $prev  = null;
    $next  = null;
    $count = count( $ordered );

    for ( $i = 0; $i < $count; $i++ ) {
        if ( (int) $ordered[ $i ]['id'] === (int) $current_id ) {
            if ( $i > 0 )        $prev = $ordered[ $i - 1 ];
            if ( $i < $count - 1 ) $next = $ordered[ $i + 1 ];
            break;
        }
    }

    return array( 'prev' => $prev, 'next' => $next );
}

// Auto-apply template
add_filter( 'page_template', 'decameron_auto_template' );
function decameron_auto_template( $template ) {
    if ( is_page() && get_post_meta( get_the_ID(), '_decameron_type', true ) ) {
        $custom = get_stylesheet_directory() . '/page-decameron.php';
        if ( file_exists( $custom ) ) {
            return $custom;
        }
    }
    return $template;
}

// Add top navigation to ALL pages
add_action('wp_body_open', 'decameron_add_top_nav');
function decameron_add_top_nav() {
    get_template_part('template-parts/header');
}

// Inline script in <head> to apply saved colour-scheme class before first paint
// (prevents flash of wrong theme)
add_action( 'wp_head', 'decameron_theme_init_script', 1 );
function decameron_theme_init_script() {
    echo '<script>(function(){var t=localStorage.getItem("dec-theme");if(t==="dark")document.documentElement.classList.add("theme-dark");else if(t!=="auto")document.documentElement.classList.add("theme-light");}());</script>' . "\n";
}
