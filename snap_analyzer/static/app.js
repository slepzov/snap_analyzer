new Vue({
    el: '#analyzer_app',
    data: {
    clusters: []
    },
    created: function () {
        const vm = this;
        axios.get('/api/clusters/')
        .then(function (response){
        vm.clusters = response.data
        })
    }
}


)