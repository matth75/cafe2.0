<template>
<div class="inner">
<!-- Search -->
<section id="search" class="alt">
<form method="get" action="/search">
<input type="text" name="query" id="query" placeholder="Search" />
</form>
</section>


<!-- Menu -->
<nav id="menu">
<header class="major">
<h2>CAFE</h2>
</header>
<ul>
<li><RouterLink to="/">Maison</RouterLink></li>
<li><RouterLink to="/calendar">Agenda</RouterLink></li>
<li><RouterLink to="/kawa">Machine à Café</RouterLink></li>
<li><RouterLink to="/contact">Contact</RouterLink></li>
<li><RouterLink to="/stage">Stage</RouterLink></li>
</ul>
</nav>


<!-- Section Contact -->
<section>
<header class="major">
<h2>Contact</h2>
</header>
<p>
Tu veux demander à Thomas Rodet de nous mettre 20/20 en Génie Logiciel ?<br />
=> envoie nous un mail
</p>
<ul class="contact">
<li class="icon solid fa-envelope">
<a href="mailto:contact@sien-ens.fr">contact@domaine-cafe.fr à setup</a>
</li>
<li class="icon solid fa-home">
ENS Paris-Saclay – DER SIEN - M2FESup Intranet
</li>
</ul>
</section>


<!-- Footer -->
<footer id="footer">
<p class="copyright">
&copy; CAFE / SIEN. Design base: HTML5 UP.<br />
Version 0.1<br />
Tazz - Matthew - Pilou
</p>
</footer>
</div>
</template>


<script setup>
// Rien de spécial ici pour l'instant
</script>
