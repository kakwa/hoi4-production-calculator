<template>
  <div class="home">
    <DivisionEditor/>
    <DivisionStats/>
    <Production/>

  </div>
</template>

<script>
// @ is an alias to /src
import DivisionEditor from '@/components/DivisionEditor.vue'
import DivisionStats from '@/components/DivisionStats.vue'
import Production from '@/components/Production.vue'

export default {
  name: 'home',
  components: {
    DivisionEditor,
    DivisionStats,
    Production
  }
}
</script>
