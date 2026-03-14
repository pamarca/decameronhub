<?php
/**
 * Template Name: Decameron Bilingual
 * ADA Compliant Template
 * 
 * Note: Top navigation is added via functions.php hook
 */

$day   = get_post_meta( get_the_ID(), '_decameron_day',   true );
$type  = get_post_meta( get_the_ID(), '_decameron_type',  true );
$order = get_post_meta( get_the_ID(), '_decameron_order', true );

$subtitle = '';
if ( $type === 'prologue' )       $subtitle = 'Proemio';
elseif ( $type === 'epilogue' )   $subtitle = 'Epilogo / Epilogue';
elseif ( $type === 'day_intro' )  $subtitle = 'Day Argument';
elseif ( $type === 'introduction' ) $subtitle = 'Giornata ' . $day . ' – Introduzione / Day ' . $day . ' – Introduction';
elseif ( $type === 'conclusion' ) $subtitle = 'Giornata ' . $day . ' – Conclusione / Day ' . $day . ' – Conclusion';
elseif ( $type === 'novella' ) {
    // CRITICAL FIX: order is 2-11, novella number is 1-10
    $novella_num = $order - 1;
    $subtitle = 'Giornata ' . $day . ', Novella ' . $novella_num . ' / Day ' . $day . ', Tale ' . $novella_num;
}
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo( 'charset' ); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?php the_title(); ?> – <?php bloginfo( 'name' ); ?></title>
    <?php
    $seo_title = get_the_title() . ' – ' . get_bloginfo( 'name' );
    $seo_desc  = $subtitle ? $subtitle . ' — ' . get_bloginfo( 'name' ) : get_bloginfo( 'description' );
    $seo_url   = get_permalink();
    ?>
    <meta name="description" content="<?php echo esc_attr( $seo_desc ); ?>">
    <meta property="og:title"       content="<?php echo esc_attr( $seo_title ); ?>">
    <meta property="og:description" content="<?php echo esc_attr( $seo_desc ); ?>">
    <meta property="og:type"        content="article">
    <meta property="og:url"         content="<?php echo esc_url( $seo_url ); ?>">
    <meta name="twitter:card"        content="summary">
    <meta name="twitter:title"       content="<?php echo esc_attr( $seo_title ); ?>">
    <meta name="twitter:description" content="<?php echo esc_attr( $seo_desc ); ?>">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<!-- Skip Link wrapped in header for ADA compliance -->
<header class="screen-reader-only-header" role="banner">
    <a href="#main-content" class="skip-link">Skip to main content</a>
</header>

<!-- Top Navigation is injected here via wp_body_open hook in functions.php -->

<div class="decameron-layout">

    <!-- Sidebar Navigation -->
    <aside class="decameron-sidebar" id="dec-sidebar" role="complementary" aria-label="Decameron navigation">
        <div class="dec-nav-header">Decameron</div>
        <nav id="dec-nav">
            <!-- Populated by JS -->
        </nav>
    </aside>

    <!-- Main Content -->
    <main class="decameron-content" id="main-content" role="main">

        <?php while ( have_posts() ) : the_post(); ?>

            <h1 class="dec-page-title"><?php the_title(); ?></h1>
            <?php if ( $subtitle ) : ?>
                <p class="dec-page-subtitle"><?php echo esc_html( $subtitle ); ?></p>
            <?php endif; ?>

            <!-- Language Toggle -->
            <div class="dec-toggle-bar" id="dec-toggle-bar" role="group" aria-label="Language selection">
                <span id="toggle-label">Show:</span>
                <label class="dec-toggle-label">
                    <input type="checkbox" id="toggle-italian" checked
                           aria-labelledby="toggle-label"
                           aria-controls="decameron-text-content">
                    <span>Italiano</span>
                </label>
                <label class="dec-toggle-label">
                    <input type="checkbox" id="toggle-english" checked
                           aria-labelledby="toggle-label"
                           aria-controls="decameron-text-content">
                    <span>English</span>
                </label>
            </div>

            <!-- Bilingual Content -->
            <div class="decameron-text-content" id="decameron-text-content">
                <?php the_content(); ?>
            </div>

        <?php endwhile; ?>

        <!-- Prev / Next navigation -->
        <?php
        $adjacent = decameron_adjacent_pages( get_the_ID() );
        $prev_page = $adjacent['prev'];
        $next_page = $adjacent['next'];
        ?>
        <nav class="dec-page-nav" aria-label="Previous and next section">
            <?php if ( $prev_page ) : ?>
                <a href="<?php echo esc_url( $prev_page['url'] ); ?>"
                   class="dec-page-nav-prev" rel="prev">
                    <span class="dec-page-nav-arrow" aria-hidden="true">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="20" height="20"><path d="M15 18l-6-6 6-6"/></svg>
                    </span>
                    <span class="dec-page-nav-content">
                        <span class="dec-page-nav-label">Previous</span>
                        <span class="dec-page-nav-title"><?php echo esc_html( $prev_page['title'] ); ?></span>
                    </span>
                </a>
            <?php else : ?>
                <span class="dec-page-nav-spacer"></span>
            <?php endif; ?>

            <?php if ( $next_page ) : ?>
                <a href="<?php echo esc_url( $next_page['url'] ); ?>"
                   class="dec-page-nav-next" rel="next">
                    <span class="dec-page-nav-content">
                        <span class="dec-page-nav-label">Next</span>
                        <span class="dec-page-nav-title"><?php echo esc_html( $next_page['title'] ); ?></span>
                    </span>
                    <span class="dec-page-nav-arrow" aria-hidden="true">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="20" height="20"><path d="M9 18l6-6-6-6"/></svg>
                    </span>
                </a>
            <?php else : ?>
                <span class="dec-page-nav-spacer"></span>
            <?php endif; ?>
        </nav>

    </main>

</div>

<?php wp_footer(); ?>
</body>
</html>
