import { Component} from '@angular/core'
import { GetMapService } from './passive/get-maps.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass'],
})

export class AppComponent{
  title = 'OVision';
  constructor(private mapService: GetMapService) {  }
}
