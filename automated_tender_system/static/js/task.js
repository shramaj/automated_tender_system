/**
 * Created by sahil on 2/4/17.
 */
 $(document).ready(function() {
     $('#save').on('click', function () {
         if (this.value === 'save') {
             $("#details").show();
         }
         else {
             $("#details").hide();
         }
     });
 });