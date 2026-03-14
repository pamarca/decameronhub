<?php
/**
 * Template Name: Decameron Homepage
 * 
 * Beautiful homepage for the Decameron site
 */
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo( 'charset' ); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?php bloginfo( 'name' ); ?> – <?php bloginfo( 'description' ); ?></title>
    <?php $seo_desc = 'A bilingual digital edition of Giovanni Boccaccio\'s Decameron — all 100 tales in Italian and English side by side.'; ?>
    <meta name="description" content="<?php echo esc_attr( $seo_desc ); ?>">
    <meta property="og:title"       content="<?php bloginfo( 'name' ); ?> – A Bilingual Edition">
    <meta property="og:description" content="<?php echo esc_attr( $seo_desc ); ?>">
    <meta property="og:type"        content="website">
    <meta property="og:url"         content="<?php echo esc_url( home_url( '/' ) ); ?>">
    <meta name="twitter:card"        content="summary">
    <meta name="twitter:title"       content="<?php bloginfo( 'name' ); ?> – A Bilingual Edition">
    <meta name="twitter:description" content="<?php echo esc_attr( $seo_desc ); ?>">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<!-- Skip Link -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<!-- Top Navigation is injected via wp_body_open hook in functions.php -->

<main id="main-content" role="main">

    <!-- Hero Section -->
    <div class="dec-home-hero">
        <h1>The Decameron</h1>
        <p class="subtitle">A Bilingual Edition</p>
        <p class="author">Giovanni Boccaccio</p>
        <a href="<?php echo esc_url( home_url('/proemio-prologue/') ); ?>" class="dec-home-cta">
            Start Reading
        </a>
    </div>

    <!-- Main Content -->
    <div class="dec-home-content">

        <!-- Stats -->
        <div class="dec-home-stats">
            <div class="dec-stat">
                <div class="dec-stat-number">100</div>
                <div class="dec-stat-label">Tales</div>
            </div>
            <div class="dec-stat">
                <div class="dec-stat-number">10</div>
                <div class="dec-stat-label">Days</div>
            </div>
            <div class="dec-stat">
                <div class="dec-stat-number">2</div>
                <div class="dec-stat-label">Languages</div>
            </div>
        </div>

        <!-- About Section -->
        <section class="dec-home-section">
            <h2>About This Edition</h2>
            <p class="dec-home-intro-text">
                This digital edition presents the complete text of Giovanni Boccaccio's 
                masterpiece <em>The Decameron</em> in both Italian and English, displayed 
                side by side for easy comparison and study. Navigate through the prologue, 
                ten days of storytelling, and the epilogue using the sidebar navigation 
                on each page.
            </p>
        </section>

        <!-- Structure Section -->
        <section class="dec-home-section">
            <h2>Structure</h2>
            <div class="dec-home-grid">
                <div class="dec-home-card">
                    <h3>Prologue</h3>
                    <p>Boccaccio's introduction to the work, setting the scene for 
                    the storytelling that follows.</p>
                </div>
                <div class="dec-home-card">
                    <h3>Ten Days</h3>
                    <p>Each day contains an introduction, ten novellas told by different 
                    narrators, and a conclusion.</p>
                </div>
                <div class="dec-home-card">
                    <h3>Epilogue</h3>
                    <p>The author's conclusion, defending his work and offering final 
                    reflections.</p>
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section class="dec-home-section">
            <h2>Features</h2>
            <div class="dec-home-grid">
                <div class="dec-home-card">
                    <h3>Bilingual Text</h3>
                    <p>Italian and English side by side with toggle controls for each language.</p>
                </div>
                <div class="dec-home-card">
                    <h3>Accessible Design</h3>
                    <p>ADA compliant with keyboard navigation, screen reader support, and responsive layout.</p>
                </div>
                <div class="dec-home-card">
                    <h3>Named Entities</h3>
                    <p>People and places are highlighted and will be indexed for easy reference.</p>
                </div>
            </div>
        </section>

    </div>

</main>

<?php wp_footer(); ?>
</body>
</html>
