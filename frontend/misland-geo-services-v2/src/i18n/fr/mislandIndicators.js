export default {
  sdg_15_3_1: {
    title: 'Indicateur SDG 15.3.1',
    description: `
    La proportion de terres dégradées
 par rapport à la superficie totale des terres. Déterminée de manière binaire
 dégradé/non dégradé.La quantification est
 basée sur l'analyse des données disponibles
 La quantification est basée sur l'analyse des données disponibles pour trois sous-indicateurs (Tendances de la couverture terrestre, productivité des terres et stocks de carbone).
 couverture des terres, productivité des terres et stocks de carbone).
 selon le guide de bonnes pratiques de la CCD de mars 2021.
 pratique de la CNULCD
    `
  },
  forest_change: {
    title: 'Changement de forêt',
    description: `
    La quantification des gains/pertes de forêts
    et des points chauds d'émission de carbone est basée sur des
    des cartes mondiales à haute résolution préexistantes
    haute résolution, dérivées de la base de données Hansen Global Forest change
    des forêts. L'évaluation des zones brûlées est réalisée à l'aide de
    Landsat 8 et Sentinel 2
          `
  },
  veg_loss: {
    title: 'Perte de végétation',
    description: `
    Les points chauds de perte/gain de végétation seront
    calculés sur la base de l'observation de séries chronologiques
    d'une combinaison sélectionnée d'indices de végétation NDVI,
    MSAVI &amp ; SAVI
          `
  },
  coastal_erosion: {
    title: 'Érosion côtière',
    description: `
    Une valeur de risque est attribuée à une section du littoral
    pour chaque variable de l'IVE (Géomorphologie, Pente côtière
    côtier, élévation du niveau de la mer, taux d'érosion et d'accrétion du
    d'érosion et d'accrétion du littoral, amplitude moyenne des marées et hauteur moyenne des vagues.
    hauteur moyenne des vagues, l'indice de vulnérabilité côtière
    (I.V.C.)est calculé comme la racine carrée de la
    de la moyenne géométrique de ces valeurs, ou de la racine
    racine carrée du produit des variables classées
    divisé par le nombre total de variables
                `
  },
  desertification: {
    title: 'Désertification',
    description: `
    MEDALUS-(Mediterranean Desertification
      et d'utilisation des terres) est utilisé dans le monde entier pour
      identifier les "zones sensibles" qui sont potentiellement
      menacées par la dégradation des sols et la
      désertification.
          `
  },
  soil_erosion: {
    title: 'Érosion du sol',
    description: `
    MISLAND étudie les modèles spatiaux
    des risques d'érosion hydrique et éolienne, d'abord séparément
    séparément, puis combinés, dans la
    région d'Afrique du Nord sujette à la sécheresse
    les meilleurs ensembles de données disponibles et
    techniques de télédétection.
          `
  }
}
